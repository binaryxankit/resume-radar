import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { fetchMe, loginUser, registerUser } from '../lib/api'
import { AuthContext, type AuthContextValue } from '../lib/auth-context'
import type { User } from '../lib/api'

const TOKEN_KEY = 'resume-radar-token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      setLoading(false)
      setUser(null)
      return
    }

    let active = true
    setLoading(true)
    fetchMe(token)
      .then((current) => {
        if (active) setUser(current)
      })
      .catch(() => {
        if (active) {
          localStorage.removeItem(TOKEN_KEY)
          setToken(null)
          setUser(null)
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [token])

  const authenticate = useCallback(async (nextToken: string) => {
    const current = await fetchMe(nextToken)
    localStorage.setItem(TOKEN_KEY, nextToken)
    setToken(nextToken)
    setUser(current)
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      const nextToken = await loginUser(email, password)
      await authenticate(nextToken)
    },
    [authenticate],
  )

  const register = useCallback(
    async (email: string, password: string) => {
      await registerUser(email, password)
      const nextToken = await loginUser(email, password)
      await authenticate(nextToken)
    },
    [authenticate],
  )

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, token, loading, login, register, logout }),
    [user, token, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
