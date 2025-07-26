import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ShoppingCart, Star } from "lucide-react"
import Image from "next/image"
import { useCart } from "@/hooks/useCart"
import { useState } from "react"

import { Product } from "@/lib/api"

interface ProductRecommendationCardProps {
  product: Product
}

export default function ProductRecommendationCard({ product }: ProductRecommendationCardProps) {
  const { addItem, getItemQuantity } = useCart();
  const [isAdding, setIsAdding] = useState(false);
  const currentQuantity = getItemQuantity(product.id);

  const handleAddToCart = async () => {
    setIsAdding(true);
    try {
      addItem({
        id: product.id,
        name: product.name,
        brand: product.brand || '',
        price: product.price || 0,
        currency: product.currency || 'USD',
        image_url: product.image_urls?.[0] || "/placeholder.svg"
      });
    } catch (error) {
      console.error('Failed to add item to cart:', error);
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <Card className="w-full max-w-xs">
      <CardHeader className="p-0">
        <Image
          src={product.image_urls?.[0] || "/placeholder.svg"}
          alt={product.name}
          width={300}
          height={200}
          className="rounded-t-lg object-cover w-full h-48"
        />
      </CardHeader>
      <CardContent className="p-4 grid gap-2">
        <CardTitle className="text-lg font-semibold">{product.name}</CardTitle>
        <CardDescription className="text-sm text-muted-foreground">{product.brand}</CardDescription>
        <div className="flex items-center gap-1 text-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`h-4 w-4 ${i < product.rating ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground"}`}
            />
          ))}
          <span className="ml-1">({product.rating.toFixed(1)})</span>
        </div>
        <p className="text-xl font-bold">${product.price.toFixed(2)}</p>
        <p className="text-sm text-muted-foreground line-clamp-2">{product.description}</p>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-between items-center">
        <Button variant="outline" size="sm">
          View Details
        </Button>
        <Button 
          size="sm" 
          onClick={handleAddToCart}
          disabled={isAdding}
        >
          <ShoppingCart className="mr-2 h-4 w-4" />
          {isAdding ? 'Adding...' : currentQuantity > 0 ? `In Cart (${currentQuantity})` : 'Add to Cart'}
        </Button>
      </CardFooter>
    </Card>
  )
}
