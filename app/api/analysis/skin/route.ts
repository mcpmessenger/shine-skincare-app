import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

// --- CONFIG --------------------------------------------------------------
const VISION_ENDPOINT =
  "https://vision.googleapis.com/v1/images:annotate?key=";

// ------------------------------------------------------------------------
// Helper – convert Google Vision API response into simplified structure
// ------------------------------------------------------------------------
interface VisionResponse {
  faceAnnotations?: Array<{
    detectionConfidence?: number;
    joyLikelihood?: string;
    sorrowLikelihood?: string;
    angerLikelihood?: string;
    surpriseLikelihood?: string;
    boundingPoly?: { vertices?: Array<{ x?: number; y?: number }> };
  }>;
  imagePropertiesAnnotation?: {
    dominantColors?: { colors?: Array<any> };
  };
  labelAnnotations?: Array<{ description?: string; score?: number }>;
}

function convertVertices(
  vertices: Array<{ x?: number; y?: number }> = []
): Array<{ x: number; y: number }> {
  return vertices.map((v) => ({
    x: v.x ?? 0,
    y: v.y ?? 0,
  }));
}

function gcvToInternal(results: VisionResponse) {
  // Faces
  const faces = results.faceAnnotations ?? [];
  const faceData = faces.map((f) => ({
    confidence: f.detectionConfidence ?? 0,
    joy_likelihood: f.joyLikelihood,
    sorrow_likelihood: f.sorrowLikelihood,
    anger_likelihood: f.angerLikelihood,
    surprise_likelihood: f.surpriseLikelihood,
    bounding_poly: convertVertices(f.boundingPoly?.vertices),
  }));

  // Colors
  const colors =
    results.imagePropertiesAnnotation?.dominantColors?.colors ?? [];

  // Labels
  const labels = results.labelAnnotations?.map((l) => ({
    description: l.description ?? "",
    score: l.score ?? 0,
  })) ?? [];

  return {
    face_detection: {
      faces_found: faces.length,
      face_data: faceData,
    },
    image_properties: {
      dominant_colors: colors,
      color_count: colors.length,
    },
    label_detection: {
      labels,
      labels_found: labels.length,
    },
  };
}

//--------------------------------------------------------------------------
// Business logic – determine skin type, concerns, metrics, etc.
//--------------------------------------------------------------------------
function determineSkinType(faceDetection: any) {
  if (faceDetection.faces_found === 0) return "Combination";
  const confidence = faceDetection.face_data[0]?.confidence ?? 0.5;
  if (confidence > 0.8) return "Normal";
  if (confidence > 0.6) return "Combination";
  return "Sensitive";
}

function determineConcerns(labelDetection: any) {
  const concerns: string[] = [];
  const descriptions: string[] = labelDetection.labels.map((l: any) =>
    l.description.toLowerCase()
  );
  const mapping: Record<string, string> = {
    acne: "Acne",
    pimple: "Acne",
    blemish: "Acne",
    "dark spot": "Hyperpigmentation",
    pigment: "Hyperpigmentation",
    freckle: "Hyperpigmentation",
    wrinkle: "Fine Lines",
    line: "Fine Lines",
    dry: "Dryness",
    oily: "Oiliness",
    red: "Redness",
    sensitive: "Sensitivity",
  };
  for (const d of descriptions) {
    for (const key in mapping) {
      if (d.includes(key) && !concerns.includes(mapping[key])) {
        concerns.push(mapping[key]);
      }
    }
  }
  if (concerns.length === 0) concerns.push("Even Skin Tone", "Hydration");
  return concerns.slice(0, 3);
}

function calcMetrics(faceDetection: any) {
  const base = { hydration: 75, oiliness: 45, sensitivity: 30 };
  if (faceDetection.faces_found === 0) return base;
  const conf = faceDetection.face_data[0]?.confidence ?? 0.5;
  if (conf > 0.8) return { hydration: 85, oiliness: 35, sensitivity: 25 };
  if (conf > 0.6) return base;
  return { hydration: 65, oiliness: 55, sensitivity: 40 };
}

function generateRecommendations(skinType: string, concerns: string[]) {
  const base: Record<string, string[]> = {
    Normal: [
      "Use a gentle cleanser twice daily",
      "Apply SPF 30+ sunscreen every morning",
      "Maintain a consistent skincare routine",
    ],
    Combination: [
      "Use a gentle cleanser twice daily",
      "Apply SPF 30+ sunscreen every morning",
      "Consider a vitamin C serum for brightening",
      "Use a lightweight moisturizer for combination skin",
    ],
    Sensitive: [
      "Use fragrance-free, gentle products",
      "Patch test new products before use",
      "Avoid harsh exfoliants",
      "Use a calming moisturizer",
    ],
  };
  const recs = [...(base[skinType] ?? base["Combination"])];
  if (concerns.includes("Acne")) recs.push("Consider a salicylic acid cleanser");
  if (concerns.includes("Hyperpigmentation"))
    recs.push("Use products with niacinamide or vitamin C");
  if (concerns.includes("Fine Lines"))
    recs.push("Consider a retinol product (start slowly)");
  return recs.slice(0, 4);
}

function productRecommendations() {
  return [
    {
      name: "Gentle Foaming Cleanser",
      category: "Cleanser",
      rating: 4.5,
      price: 24.99,
      image: "/products/cleanser.jpg",
    },
    {
      name: "Vitamin C Brightening Serum",
      category: "Serum",
      rating: 4.8,
      price: 45.99,
      image: "/products/serum.jpg",
    },
    {
      name: "Lightweight Hydrating Moisturizer",
      category: "Moisturizer",
      rating: 4.3,
      price: 32.99,
      image: "/products/moisturizer.jpg",
    },
  ];
}

//--------------------------------------------------------------------------
// POST handler – accepts multipart/form-data with "image" field
//--------------------------------------------------------------------------
export async function POST(request: NextRequest) {
  try {
    const apiKey = process.env.GOOGLE_VISION_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: "GOOGLE_VISION_API_KEY env var not set" },
        { status: 500 }
      );
    }

    const formData = await request.formData();
    const image = formData.get("image") as File | null;

    if (!image) {
      return NextResponse.json(
        { error: "No image provided" },
        { status: 400 }
      );
    }

    // Convert File → base64
    const buffer = Buffer.from(await image.arrayBuffer());
    const base64Image = buffer.toString("base64");

    // Call Google Vision REST API
    const visionBody = {
      requests: [
        {
          image: { content: base64Image },
          features: [
            { type: "FACE_DETECTION" },
            { type: "IMAGE_PROPERTIES" },
            { type: "LABEL_DETECTION", maxResults: 20 },
          ],
        },
      ],
    };

    const visionRes = await fetch(VISION_ENDPOINT + apiKey, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(visionBody),
    });

    if (!visionRes.ok) {
      const errText = await visionRes.text();
      return NextResponse.json(
        { error: "Google Vision API error", details: errText },
        { status: 500 }
      );
    }

    const visionJson = await visionRes.json();
    const annotation =
      visionJson.responses?.[0] ?? ({} as Record<string, any>);
    const converted = gcvToInternal(annotation as VisionResponse);

    // Pump through business logic
    const skinType = determineSkinType(converted.face_detection);
    const concerns = determineConcerns(converted.label_detection);
    const metrics = calcMetrics(converted.face_detection);
    const recs = generateRecommendations(skinType, concerns);
    const products = productRecommendations();

    return NextResponse.json({
      status: "success",
      skinType,
      concerns,
      hydration: metrics.hydration,
      oiliness: metrics.oiliness,
      sensitivity: metrics.sensitivity,
      recommendations: recs,
      products,
    });
  } catch (err) {
    console.error("Analysis route error", err);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 