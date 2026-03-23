export const isProd = process.env.NODE_ENV === 'production'
export const baseURL = isProd ? 'http://localhost:16088' : '/api'
export const baseHost = isProd ? 'localhost:16088' : location.host
export const baseOrigin = isProd ? 'http://localhost:16088' : location.origin