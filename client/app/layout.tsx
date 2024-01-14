import { Inter } from "next/font/google"
import { cookies } from "next/headers"
import { ReactNode } from "react"
import { Toaster } from "@/components/ui/sonner"
import { Providers } from "@/components/utility/providers"
import { GlobalState } from "@/components/utility/global-state"
import "./globals.css"
import { createServerClient } from "@supabase/ssr"
import { Database } from "@/supabase/types"

const inter = Inter({ subsets: ["latin"] }) // font preloading

interface RootLayoutProps {
  children: ReactNode
}

export default async function RootLayout({ children }: RootLayoutProps) {
  const cookieStore = cookies()
  const supabase = createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          console.log(cookieStore.get(name))
          return cookieStore.get(name)?.value
        }
      }
    }
  )
  const session = (await supabase.auth.getSession()).data.session

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers attribute="class" defaultTheme="dark">
          <Toaster richColors position="top-center" duration={2000} />
          <div className="bg-background text-foreground flex h-screen flex-col items-center">
            {session ? <GlobalState>{children}</GlobalState> : children}
          </div>
        </Providers>
      </body>
    </html>
  )
}
