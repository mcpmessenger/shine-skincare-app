import { Product } from '@/hooks/useCart'

export const products: Product[] = [
  {
    id: 'is-clinical-cleansing',
    name: 'iS Clinical Cleansing Complex',
    price: 45.00,
    image: '/api/images/products/is-clinical-cleansing.jpg',
    description: 'Gentle yet effective cleanser with salicylic acid for acne-prone skin',
    category: 'cleanser'
  },
  {
    id: 'dermalogica-ultracalming',
    name: 'Dermalogica UltraCalming Cleanser',
    price: 38.00,
    image: '/api/images/products/dermalogica-ultracalming.webp',
    description: 'Soothing cleanser for sensitive and reactive skin',
    category: 'cleanser'
  },
  {
    id: 'skinceuticals-ce-ferulic',
    name: 'SkinCeuticals C E Ferulic',
    price: 169.00,
    image: '/api/images/products/skinceuticals-ce-ferulic.webp',
    description: 'Antioxidant serum with vitamin C for brightening and protection',
    category: 'serum'
  },
  {
    id: 'tns-advanced-serum',
    name: 'TNS Advanced+ Serum',
    price: 195.00,
    image: '/api/images/products/TNS_Advanced+_Serum_1oz_2_FullWidth.jpg',
    description: 'Advanced growth factor serum for anti-aging and skin renewal',
    category: 'serum'
  },
  {
    id: 'pca-skin-pigment-gel',
    name: 'PCA SKIN Pigment Gel Pro',
    price: 89.00,
    image: '/api/images/products/pca-skin-pigment-gel.jpg',
    description: 'Professional-grade treatment for hyperpigmentation and dark spots',
    category: 'treatment'
  },
  {
    id: 'first-aid-beauty-repair',
    name: 'First Aid Beauty Ultra Repair Cream',
    price: 34.00,
    image: '/api/images/products/first-aid-beauty-repair.webp',
    description: 'Intensive moisturizer for dry, sensitive skin',
    category: 'moisturizer'
  },
  {
    id: 'eltamd-uv-clear',
    name: 'EltaMD UV Clear Broad-Spectrum SPF 46',
    price: 39.00,
    image: '/api/images/products/eltamd-uv-clear.webp',
    description: 'Oil-free sunscreen with niacinamide for acne-prone skin',
    category: 'sunscreen'
  },
  {
    id: 'allies-of-skin-cleanser',
    name: 'Allies of Skin Molecular Silk Amino Hydrating Cleanser',
    price: 52.00,
    image: '/api/images/products/Allies of Skin Molecular Silk Amino Hydrating Cleanser.webp',
    description: 'Luxury cleanser with amino acids for gentle yet effective cleansing',
    category: 'cleanser'
  },
  {
    id: 'naturopathica-calendula',
    name: 'Naturopathica Calendula Essential Hydrating Cream',
    price: 58.00,
    image: '/api/images/products/Naturopathica Calendula Essential Hydrating Cream.webp',
    description: 'Calming moisturizer with calendula for sensitive skin',
    category: 'moisturizer'
  },
  {
    id: 'obagi-clenziderm',
    name: 'Obagi CLENZIderm M.D. System (Therapeutic Lotion)',
    price: 42.00,
    image: '/api/images/products/Obagi CLENZIderm M.D. System (Therapeutic Lotion).webp',
    description: 'Medical-grade acne treatment system',
    category: 'treatment'
  }
]

export const getProductsByCategory = (category: string) => {
  return products.filter(product => product.category === category)
}

export const getProductById = (id: string) => {
  return products.find(product => product.id === id)
} 