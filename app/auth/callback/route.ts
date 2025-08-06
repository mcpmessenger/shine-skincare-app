import { createSupabaseServerClient } from '@/lib/supabase'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createSupabaseServerClient()
    
    try {
      const { data, error } = await supabase.auth.exchangeCodeForSession(code)
      
      if (error) {
        console.error('Error exchanging code for session:', error)
        return NextResponse.redirect(`${requestUrl.origin}/auth/error`)
      }

      if (data.user) {
        // Check if user exists in our users table
        const { data: existingUser, error: userError } = await supabase
          .from('users')
          .select('*')
          .eq('id', data.user.id)
          .single()

        if (userError && userError.code === 'PGRST116') {
          // User doesn't exist, create new user record
          const { error: insertError } = await supabase
            .from('users')
            .insert({
              id: data.user.id,
              email: data.user.email!,
              name: data.user.user_metadata.full_name || data.user.email!.split('@')[0],
              profile_picture_url: data.user.user_metadata.avatar_url,
              google_id: data.user.user_metadata.sub,
              last_login_at: new Date().toISOString(),
            })

          if (insertError) {
            console.error('Error creating user record:', insertError)
          }
        } else if (!userError) {
          // User exists, update last login
          await supabase
            .from('users')
            .update({ 
              last_login_at: new Date().toISOString(),
              profile_picture_url: data.user.user_metadata.avatar_url,
              name: data.user.user_metadata.full_name || existingUser.name,
            })
            .eq('id', data.user.id)
        }
      }

      return NextResponse.redirect(`${requestUrl.origin}/`)
    } catch (error) {
      console.error('Unexpected error in auth callback:', error)
      return NextResponse.redirect(`${requestUrl.origin}/auth/error`)
    }
  }

  return NextResponse.redirect(`${requestUrl.origin}/auth/error`)
} 