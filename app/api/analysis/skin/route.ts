import { NextRequest, NextResponse } from "next/server";
import { products } from "@/lib/products";

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

function getIntelligentProductRecommendations(skinType: string, concerns: string[], metrics: any) {
  // Define product matching rules based on skin analysis
  const matchingRules = {
    // Skin Type based recommendations
    Normal: {
      priority: ['cleanser', 'moisturizer', 'sunscreen'],
      avoid: []
    },
    Combination: {
      priority: ['cleanser', 'serum', 'moisturizer', 'sunscreen'],
      avoid: ['heavy moisturizers']
    },
    Sensitive: {
      priority: ['cleanser', 'moisturizer'],
      avoid: ['harsh treatments', 'fragranced products']
    },
    Dry: {
      priority: ['cleanser', 'serum', 'moisturizer'],
      avoid: ['drying cleansers']
    },
    Oily: {
      priority: ['cleanser', 'serum', 'moisturizer'],
      avoid: ['heavy moisturizers']
    }
  };

  // Concern-based recommendations
  const concernMatches = {
    Acne: {
      categories: ['cleanser', 'treatment'],
      keywords: ['salicylic acid', 'acne', 'therapeutic', 'medical-grade'],
      avoid: ['heavy', 'comedogenic']
    },
    Hyperpigmentation: {
      categories: ['serum', 'treatment'],
      keywords: ['vitamin C', 'niacinamide', 'brightening', 'pigment'],
      avoid: []
    },
    'Fine Lines': {
      categories: ['serum', 'treatment'],
      keywords: ['retinol', 'growth factor', 'anti-aging', 'renewal'],
      avoid: []
    },
    Sensitivity: {
      categories: ['cleanser', 'moisturizer'],
      keywords: ['gentle', 'calming', 'soothing', 'ultracalming'],
      avoid: ['harsh', 'exfoliating', 'fragranced']
    },
    Dehydration: {
      categories: ['serum', 'moisturizer'],
      keywords: ['hydrating', 'moisturizing', 'amino acids', 'hyaluronic'],
      avoid: ['drying', 'astringent']
    }
  };

  // Score products based on analysis results
  const scoredProducts = products.map(product => {
    let score = 0;
    let reasons: string[] = [];

    // Base score for skin type compatibility
    const skinTypeRule = matchingRules[skinType as keyof typeof matchingRules];
    if (skinTypeRule) {
      if (skinTypeRule.priority.includes(product.category)) {
        score += 10;
        reasons.push(`Good for ${skinType} skin`);
      }
      if (skinTypeRule.avoid.some(avoid => 
        product.description.toLowerCase().includes(avoid.toLowerCase()) ||
        product.name.toLowerCase().includes(avoid.toLowerCase())
      )) {
        score -= 5;
        reasons.push(`May not be ideal for ${skinType} skin`);
      }
    }

    // Score based on concerns
    concerns.forEach(concern => {
      const concernRule = concernMatches[concern as keyof typeof concernMatches];
      if (concernRule) {
        if (concernRule.categories.includes(product.category)) {
          score += 8;
          reasons.push(`Targets ${concern.toLowerCase()}`);
        }
        if (concernRule.keywords.some(keyword => 
          product.description.toLowerCase().includes(keyword.toLowerCase()) ||
          product.name.toLowerCase().includes(keyword.toLowerCase())
        )) {
          score += 6;
          reasons.push(`Contains ingredients for ${concern.toLowerCase()}`);
        }
        if (concernRule.avoid.some(avoid => 
          product.description.toLowerCase().includes(avoid.toLowerCase()) ||
          product.name.toLowerCase().includes(avoid.toLowerCase())
        )) {
          score -= 3;
          reasons.push(`May aggravate ${concern.toLowerCase()}`);
        }
      }
    });

    // Score based on metrics
    if (metrics.hydration < 70 && product.category === 'moisturizer') {
      score += 5;
      reasons.push('Addresses hydration needs');
    }
    if (metrics.oiliness > 60 && product.category === 'cleanser') {
      score += 4;
      reasons.push('Helps control oil');
    }
    if (metrics.sensitivity > 50 && product.description.toLowerCase().includes('gentle')) {
      score += 3;
      reasons.push('Gentle for sensitive skin');
    }

    // Category balance - ensure we have a good mix
    if (product.category === 'cleanser') score += 2; // Everyone needs a cleanser
    if (product.category === 'sunscreen') score += 3; // Sun protection is crucial

    return {
      ...product,
      score,
      reasons,
      rating: 4.5 + (score * 0.1) // Adjust rating based on score
    };
  });

  // Sort by score and return top recommendations
  const topProducts = scoredProducts
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
    .map(product => ({
      name: product.name,
      category: product.category,
      rating: Math.min(5.0, Math.max(4.0, product.rating)), // Keep rating between 4.0-5.0
      price: product.price,
      image: product.image,
      matchReason: product.reasons[0] || 'Recommended for your skin profile',
      score: product.score
    }));

  return topProducts;
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
    const products = getIntelligentProductRecommendations(skinType, concerns, metrics);

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