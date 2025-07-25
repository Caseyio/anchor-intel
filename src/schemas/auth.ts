// src/schemas/auth.ts
import { z } from 'zod'

export const UserCreateSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
  role: z.enum(['admin', 'cashier']),
})

export const LoginInputSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
})

export const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.literal('bearer'),
})

export const UserOutSchema = z.object({
  id: z.number(),
  username: z.string(),
  role: z.string(),
})

export type UserCreate = z.infer<typeof UserCreateSchema>
export type LoginInput = z.infer<typeof LoginInputSchema>
export type TokenResponse = z.infer<typeof TokenResponseSchema>
export type UserOut = z.infer<typeof UserOutSchema>

export function validateUserOut(data: unknown): UserOut | null {
  const result = UserOutSchema.safeParse(data)
  return result.success ? result.data : null
}
