'use client';

import { ShoppingCart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useCart } from '@/hooks/useCart';
import { useState } from 'react';
import { CartDrawer } from './cart-drawer';

export function CartIcon() {
  const { state } = useCart();
  const [isCartOpen, setIsCartOpen] = useState(false);

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="relative"
        onClick={() => setIsCartOpen(true)}
      >
        <ShoppingCart className="h-5 w-5" />
        {state.itemCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
          >
            {state.itemCount > 99 ? '99+' : state.itemCount}
          </Badge>
        )}
        <span className="sr-only">Cart</span>
      </Button>
      
      <CartDrawer 
        open={isCartOpen} 
        onOpenChange={setIsCartOpen} 
      />
    </>
  );
} 