import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Vérifier si l'utilisateur accède à une route admin
  if (request.nextUrl.pathname.startsWith('/admin')) {
    // Vérifier si l'utilisateur est authentifié via le cookie
    const isAuthenticated = request.cookies.get('auth0.is.authenticated')?.value === 'true';
    
    if (!isAuthenticated) {
      // Rediriger vers la page d'accueil avec le paramètre returnTo
      const url = new URL('/', request.url);
      url.searchParams.set('returnTo', request.nextUrl.pathname);
      return NextResponse.redirect(url);
    }
  }
  
  return NextResponse.next()
}

// Configurer les chemins sur lesquels le middleware doit s'exécuter
export const config = {
  matcher: ['/admin/:path*'],
} 