'use client'

import { createContext, useContext, useReducer, ReactNode, useEffect } from 'react'
import { useAuth } from './useAuth'
import { CartService } from '@/lib/cart-service'

export interface Product {
  id: string
  name: string
  price: number
  image: string
  description: string
  category: string
}

export interface CartItem extends Product {
  quantity: number
}

interface CartState {
  items: CartItem[]
  total: number
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: Product }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_CART'; payload: { items: CartItem[]; total: number } }

const CartContext = createContext<{
  state: CartState
  dispatch: React.Dispatch<CartAction>
  isAuthenticated: boolean
  showSignInModal: () => void
} | null>(null)

const cartReducer = (state: CartState, action: CartAction): CartState => {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingItem = state.items.find(item => item.id === action.payload.id)
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          ),
          total: state.total + action.payload.price
        }
      }
      return {
        ...state,
        items: [...state.items, { ...action.payload, quantity: 1 }],
        total: state.total + action.payload.price
      }
    }
    case 'REMOVE_ITEM': {
      const item = state.items.find(item => item.id === action.payload)
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload),
        total: state.total - (item ? item.price * item.quantity : 0)
      }
    }
    case 'UPDATE_QUANTITY': {
      const item = state.items.find(item => item.id === action.payload.id)
      if (!item) return state
      
      const quantityDiff = action.payload.quantity - item.quantity
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        ),
        total: state.total + (item.price * quantityDiff)
      }
    }
    case 'CLEAR_CART':
      return {
        items: [],
        total: 0
      }
    case 'LOAD_CART':
      return {
        items: action.payload.items,
        total: action.payload.total
      }
    default:
      return state
  }
}

export const CartProvider = ({ children }: { children: ReactNode }) => {
  const { state: authState } = useAuth()
  const [state, dispatch] = useReducer(cartReducer, {
    items: [],
    total: 0
  })

  // Load cart from Supabase when user is authenticated
  useEffect(() => {
            if (authState.isAuthenticated && authState.user) {
          const loadCart = async () => {
            try {
              const cartData = await CartService.getUserCart(authState.user!.id)
          if (cartData && cartData.items.length > 0) {
            dispatch({ type: 'LOAD_CART', payload: cartData })
          }
        } catch (error) {
          console.error('Error loading cart from Supabase:', error)
        }
      }
      loadCart()
    }
  }, [authState.isAuthenticated, authState.user])

  // Save cart to Supabase when cart changes and user is authenticated
  useEffect(() => {
    if (authState.isAuthenticated && authState.user && state.items.length > 0) {
      const saveCart = async () => {
        try {
          await CartService.saveCart(authState.user!.id, state.items, state.total)
        } catch (error) {
          console.error('Error saving cart to Supabase:', error)
        }
      }
      saveCart()
    }
  }, [state.items, state.total, authState.isAuthenticated, authState.user])

  const showSignInModal = () => {
    // This will be handled by the component that uses the cart
    // The modal will be shown when trying to add items without authentication
  }

  return (
    <CartContext.Provider value={{ 
      state, 
      dispatch, 
      isAuthenticated: authState.isAuthenticated,
      showSignInModal 
    }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => {
  const context = useContext(CartContext)
  if (!context) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
} 