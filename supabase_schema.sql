-- Shine Skincare App Database Schema
-- This file contains all the necessary tables for the e-commerce functionality

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    google_id TEXT UNIQUE,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    profile_picture_url TEXT,
    phone_number TEXT,
    date_of_birth DATE,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    shipping_address JSONB,
    billing_address JSONB,
    marketing_preferences JSONB DEFAULT '{}',
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    category TEXT NOT NULL,
    brand TEXT,
    sku TEXT UNIQUE,
    barcode TEXT,
    weight DECIMAL(8,3),
    dimensions JSONB,
    images TEXT[],
    ingredients TEXT[],
    usage_instructions TEXT,
    skin_type_compatibility TEXT[],
    skin_concerns_addressed TEXT[],
    dermatologist_recommended BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    order_number TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
    payment_method TEXT,
    payment_intent_id TEXT,
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    estimated_delivery_date DATE,
    tracking_number TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Carts table
CREATE TABLE IF NOT EXISTS carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cart items table
CREATE TABLE IF NOT EXISTS cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Abandoned carts table
CREATE TABLE IF NOT EXISTS abandoned_carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_email TEXT NOT NULL,
    user_name TEXT NOT NULL,
    cart_items JSONB NOT NULL,
    cart_total DECIMAL(10,2) NOT NULL,
    abandoned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    email_sent_count INTEGER DEFAULT 0,
    last_email_sent_at TIMESTAMP WITH TIME ZONE,
    next_email_scheduled_at TIMESTAMP WITH TIME ZONE,
    is_recovered BOOLEAN DEFAULT false,
    recovered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email campaigns table
CREATE TABLE IF NOT EXISTS email_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_email TEXT NOT NULL,
    campaign_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skin analysis results table
CREATE TABLE IF NOT EXISTS skin_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    image_url TEXT,
    analysis_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product recommendations table
CREATE TABLE IF NOT EXISTS product_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    analysis_result_id UUID REFERENCES skin_analysis_results(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    recommendation_score DECIMAL(3,2),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_abandoned_carts_user_id ON abandoned_carts(user_id);
CREATE INDEX IF NOT EXISTS idx_abandoned_carts_is_recovered ON abandoned_carts(is_recovered);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_carts_updated_at BEFORE UPDATE ON carts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cart_items_updated_at BEFORE UPDATE ON cart_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_abandoned_carts_updated_at BEFORE UPDATE ON abandoned_carts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE abandoned_carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE skin_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_recommendations ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON users FOR INSERT WITH CHECK (auth.uid() = id);

-- Products policies (public read, admin write)
CREATE POLICY "Anyone can view active products" ON products FOR SELECT USING (is_active = true);
CREATE POLICY "Admin can manage products" ON products FOR ALL USING (auth.role() = 'service_role');

-- Orders policies
CREATE POLICY "Users can view own orders" ON orders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own orders" ON orders FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Admin can manage orders" ON orders FOR ALL USING (auth.role() = 'service_role');

-- Order items policies
CREATE POLICY "Users can view own order items" ON order_items FOR SELECT USING (
    EXISTS (SELECT 1 FROM orders WHERE orders.id = order_items.order_id AND orders.user_id = auth.uid())
);
CREATE POLICY "Admin can manage order items" ON order_items FOR ALL USING (auth.role() = 'service_role');

-- Carts policies
CREATE POLICY "Users can manage own cart" ON carts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Session-based cart access" ON carts FOR ALL USING (session_id IS NOT NULL);

-- Cart items policies
CREATE POLICY "Users can manage own cart items" ON cart_items FOR ALL USING (
    EXISTS (SELECT 1 FROM carts WHERE carts.id = cart_items.cart_id AND carts.user_id = auth.uid())
);
CREATE POLICY "Session-based cart items access" ON cart_items FOR ALL USING (
    EXISTS (SELECT 1 FROM carts WHERE carts.id = cart_items.cart_id AND carts.session_id IS NOT NULL)
);

-- Abandoned carts policies (admin only)
CREATE POLICY "Admin can manage abandoned carts" ON abandoned_carts FOR ALL USING (auth.role() = 'service_role');

-- Email campaigns policies (admin only)
CREATE POLICY "Admin can manage email campaigns" ON email_campaigns FOR ALL USING (auth.role() = 'service_role');

-- Skin analysis results policies
CREATE POLICY "Users can view own analysis results" ON skin_analysis_results FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own analysis results" ON skin_analysis_results FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Admin can manage analysis results" ON skin_analysis_results FOR ALL USING (auth.role() = 'service_role');

-- Product recommendations policies
CREATE POLICY "Users can view own recommendations" ON product_recommendations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Admin can manage recommendations" ON product_recommendations FOR ALL USING (auth.role() = 'service_role');

-- Insert sample products
INSERT INTO products (name, description, price, category, brand, ingredients, skin_type_compatibility, skin_concerns_addressed, dermatologist_recommended) VALUES
('Gentle Cleanser', 'A mild, non-irritating cleanser suitable for all skin types', 24.99, 'Cleanser', 'Shine', ARRAY['Glycerin', 'Hyaluronic Acid', 'Ceramides'], ARRAY['All Skin Types'], ARRAY['Dryness', 'Sensitivity'], true),
('Hydrating Serum', 'Intensive hydration serum with hyaluronic acid', 34.99, 'Serum', 'Shine', ARRAY['Hyaluronic Acid', 'Niacinamide', 'Peptides'], ARRAY['Dry', 'Normal', 'Combination'], ARRAY['Dryness', 'Fine Lines'], true),
('SPF 30 Moisturizer', 'Broad-spectrum protection with hydration', 29.99, 'Sunscreen', 'Shine', ARRAY['Zinc Oxide', 'Titanium Dioxide', 'Glycerin'], ARRAY['All Skin Types'], ARRAY['Sun Damage', 'Aging'], true),
('Retinol Night Cream', 'Anti-aging night treatment with retinol', 44.99, 'Night Cream', 'Shine', ARRAY['Retinol', 'Peptides', 'Ceramides'], ARRAY['Normal', 'Dry'], ARRAY['Fine Lines', 'Wrinkles', 'Uneven Texture'], true),
('Acne Spot Treatment', 'Targeted treatment for blemishes', 19.99, 'Treatment', 'Shine', ARRAY['Salicylic Acid', 'Tea Tree Oil', 'Zinc'], ARRAY['Oily', 'Combination'], ARRAY['Acne', 'Blemishes'], true);

-- Create function to generate order numbers
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TEXT AS $$
DECLARE
    order_num TEXT;
BEGIN
    SELECT 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(COALESCE(MAX(SUBSTRING(order_number FROM 16)), '0')::INTEGER + 1, 4, '0')
    INTO order_num
    FROM orders
    WHERE order_number LIKE 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-%';
    
    RETURN COALESCE(order_num, 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-0001');
END;
$$ LANGUAGE plpgsql; 