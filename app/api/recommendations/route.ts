import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const skinType = searchParams.get('skinType');
    const concerns = searchParams.get('concerns');
    const healthScore = searchParams.get('healthScore');

    // Enhanced recommendations based on skin analysis
    const enhancedRecommendations = generateEnhancedRecommendations(
      skinType || 'combination',
      concerns ? concerns.split(',') : [],
      parseFloat(healthScore || '0.7')
    );

    return NextResponse.json({
      message: 'Enhanced recommendations generated',
      recommendations: enhancedRecommendations.products,
      skincare_routine: enhancedRecommendations.routine,
      general_tips: enhancedRecommendations.tips,
      confidence_score: enhancedRecommendations.confidence,
      analysis_based: true
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

function generateEnhancedRecommendations(
  skinType: string, 
  concerns: string[], 
  healthScore: number
) {
  // Product database with ingredients and skin concerns
  const products = [
    {
      id: 'is-clinical-cleansing',
      name: 'iS Clinical Cleansing Complex',
      brand: 'iS Clinical',
      price: 45.00,
      category: 'cleanser',
      description: 'Gentle yet effective cleanser with salicylic acid for acne-prone skin',
      ingredients: ['salicylic acid', 'glycolic acid', 'vitamin c', 'aloe vera'],
      skinType: ['oily', 'combination', 'acne-prone'],
      concerns: ['acne', 'clogged_pores', 'uneven_texture'],
      dermatologist_recommended: true,
      rating: 4.8
    },
    {
      id: 'dermalogica-ultracalming',
      name: 'Dermalogica UltraCalming Cleanser',
      brand: 'Dermalogica',
      price: 38.00,
      category: 'cleanser',
      description: 'Soothing cleanser for sensitive and reactive skin',
      ingredients: ['oat kernel extract', 'colloidal oatmeal', 'aloe vera', 'chamomile'],
      skinType: ['sensitive', 'dry', 'reactive'],
      concerns: ['redness', 'irritation', 'sensitivity'],
      dermatologist_recommended: true,
      rating: 4.7
    },
    {
      id: 'skinceuticals-ce-ferulic',
      name: 'SkinCeuticals C E Ferulic',
      brand: 'SkinCeuticals',
      price: 169.00,
      category: 'serum',
      description: 'Antioxidant serum with vitamin C for brightening and protection',
      ingredients: ['vitamin c', 'vitamin e', 'ferulic acid', 'hyaluronic acid'],
      skinType: ['all'],
      concerns: ['dark_spots', 'hyperpigmentation', 'aging', 'sun_damage'],
      dermatologist_recommended: true,
      rating: 4.9
    },
    {
      id: 'tns-advanced-serum',
      name: 'TNS Advanced+ Serum',
      brand: 'SkinMedica',
      price: 195.00,
      category: 'serum',
      description: 'Advanced growth factor serum for anti-aging and skin renewal',
      ingredients: ['growth factors', 'peptides', 'hyaluronic acid', 'antioxidants'],
      skinType: ['all'],
      concerns: ['aging', 'fine_lines', 'wrinkles', 'texture'],
      dermatologist_recommended: true,
      rating: 4.8
    },
    {
      id: 'pca-skin-pigment-gel',
      name: 'PCA SKIN Pigment Gel Pro',
      brand: 'PCA SKIN',
      price: 89.00,
      category: 'treatment',
      description: 'Professional-grade treatment for hyperpigmentation and dark spots',
      ingredients: ['hydroquinone', 'kojic acid', 'vitamin c', 'niacinamide'],
      skinType: ['all'],
      concerns: ['dark_spots', 'hyperpigmentation', 'melasma'],
      dermatologist_recommended: true,
      rating: 4.6
    },
    {
      id: 'first-aid-beauty-repair',
      name: 'First Aid Beauty Ultra Repair Cream',
      brand: 'First Aid Beauty',
      price: 34.00,
      category: 'moisturizer',
      description: 'Intensive moisturizer for dry, sensitive skin',
      ingredients: ['ceramides', 'hyaluronic acid', 'shea butter', 'colloidal oatmeal'],
      skinType: ['dry', 'sensitive', 'dehydrated'],
      concerns: ['dryness', 'irritation', 'barrier_damage'],
      dermatologist_recommended: true,
      rating: 4.7
    },
    {
      id: 'eltamd-uv-clear',
      name: 'EltaMD UV Clear Broad-Spectrum SPF 46',
      brand: 'EltaMD',
      price: 39.00,
      category: 'sunscreen',
      description: 'Oil-free sunscreen with niacinamide for acne-prone skin',
      ingredients: ['zinc oxide', 'niacinamide', 'hyaluronic acid', 'vitamin e'],
      skinType: ['all', 'acne-prone', 'sensitive'],
      concerns: ['sun_damage', 'acne', 'redness'],
      dermatologist_recommended: true,
      rating: 4.8
    }
  ];

  // Score products based on skin type, concerns, and health score
  const scoredProducts = products.map(product => {
    let score = 0;
    const reasons: string[] = [];

    // Skin type compatibility
    if (product.skinType.includes(skinType) || product.skinType.includes('all')) {
      score += 3;
      reasons.push(`Suitable for ${skinType} skin`);
    }

    // Concern matching
    concerns.forEach(concern => {
      if (product.concerns.includes(concern)) {
        score += 4;
        reasons.push(`Addresses ${concern}`);
      }
    });

    // Health score adjustment
    if (healthScore < 0.6) {
      // Prioritize gentle, barrier-repair products for poor skin health
      if (product.ingredients.some(ing => ['ceramides', 'hyaluronic acid', 'aloe vera'].includes(ing))) {
        score += 2;
        reasons.push('Barrier-repair ingredients');
      }
    }

    // Dermatologist recommendation bonus
    if (product.dermatologist_recommended) {
      score += 1;
      reasons.push('Dermatologist recommended');
    }

    // Rating bonus
    score += (product.rating - 4.0) * 2;

    return { ...product, score, reasons };
  });

  // Sort by score and get top recommendations
  const topProducts = scoredProducts
    .sort((a, b) => b.score - a.score)
    .slice(0, 6);

  // Generate skincare routine
  const routine = generateSkincareRoutine(topProducts);

  // Generate general tips based on health score
  const tips = generateGeneralTips(healthScore, concerns);

  // Calculate confidence score
  const confidence = Math.min(1.0, Math.max(0.3, healthScore + (concerns.length * 0.1)));

  return {
    products: topProducts,
    routine,
    tips,
    confidence
  };
}

function generateSkincareRoutine(products: any[]) {
  const morning: any[] = [];
  const evening: any[] = [];

  // Categorize products by time of day
  products.forEach(product => {
    if (product.category === 'cleanser') {
      morning.push(product);
      evening.push(product);
    } else if (product.category === 'serum') {
      morning.push(product);
      evening.push(product);
    } else if (product.category === 'moisturizer') {
      morning.push(product);
      evening.push(product);
    } else if (product.category === 'sunscreen') {
      morning.push(product);
    } else if (product.category === 'treatment') {
      evening.push(product);
    }
  });

  return {
    morning: morning.slice(0, 3).map((product, index) => ({
      step: index + 1,
      product: product.name,
      category: product.category,
      instructions: getInstructions(product.category, 'morning')
    })),
    evening: evening.slice(0, 3).map((product, index) => ({
      step: index + 1,
      product: product.name,
      category: product.category,
      instructions: getInstructions(product.category, 'evening')
    }))
  };
}

function getInstructions(category: string, time: string): string {
  const instructions: { [key: string]: { [key: string]: string } } = {
    cleanser: {
      morning: 'Apply to damp skin and rinse thoroughly',
      evening: 'Apply to damp skin and rinse thoroughly'
    },
    serum: {
      morning: 'Apply a small amount and gently pat into skin',
      evening: 'Apply a small amount and gently pat into skin'
    },
    moisturizer: {
      morning: 'Apply to slightly damp skin',
      evening: 'Apply to slightly damp skin'
    },
    sunscreen: {
      morning: 'Apply generously and reapply every 2 hours',
      evening: 'Not needed in evening'
    },
    treatment: {
      morning: 'Use as directed, typically 2-3 times per week',
      evening: 'Use as directed, typically 2-3 times per week'
    }
  };

  return instructions[category]?.[time] || 'Use as directed';
}

function generateGeneralTips(healthScore: number, concerns: string[]): string[] {
  const tips: string[] = [];

  if (healthScore >= 0.8) {
    tips.push('Continue your current skincare routine');
    tips.push('Maintain good hydration and nutrition');
    tips.push('Use broad-spectrum sunscreen daily');
    tips.push('Consider preventive anti-aging products');
  } else if (healthScore >= 0.6) {
    tips.push('Focus on gentle, consistent skincare');
    tips.push('Address specific concerns with targeted products');
    tips.push('Maintain skin barrier health');
    tips.push('Use sunscreen to prevent further damage');
  } else {
    tips.push('Consider consulting with a dermatologist');
    tips.push('Focus on gentle, barrier-repair products');
    tips.push('Avoid harsh ingredients and over-exfoliation');
    tips.push('Prioritize hydration and protection');
  }

  // Add concern-specific tips
  if (concerns.includes('acne')) {
    tips.push('Avoid touching face throughout the day');
    tips.push('Use non-comedogenic products');
  }
  if (concerns.includes('redness')) {
    tips.push('Avoid hot water when washing face');
    tips.push('Use fragrance-free products');
  }
  if (concerns.includes('dark_spots')) {
    tips.push('Use broad-spectrum sunscreen daily');
    tips.push('Avoid picking at blemishes');
  }

  return tips.slice(0, 6); // Limit to 6 tips
} 