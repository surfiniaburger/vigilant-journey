import { memo } from "react"

export const Response = memo(
  ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  (prevProps, nextProps) => prevProps.children === nextProps.children
)

Response.displayName = "Response"
