Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
API Reference
Directives
Components
File-system conventions
Functions
Configuration
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
Fetching data
Server Components
With the fetch API
With an ORM or database
Client Components
Streaming data with the use hook
Community libraries
Deduplicate requests and cache data
Streaming
With loading.js
With <Suspense>
Creating meaningful loading states
Examples
Sequential data fetching
Parallel data fetching
Preloading data
API Reference
Edit this page on GitHub
Scroll to top
App Router
Getting Started
Fetching Data
Fetching Data
This page will walk you through how you can fetch data in Server and Client Components, and how to stream components that depend on data.

Fetching data
Server Components
You can fetch data in Server Components using:

The fetch API
An ORM or database
With the fetch API
To fetch data with the fetch API, turn your component into an asynchronous function, and await the fetch call. For example:

app/blog/page.tsx
TypeScript

TypeScript

export default async function Page() {
  const data = await fetch('https://api.vercel.app/blog')
  const posts = await data.json()
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
Good to know:

fetch responses are not cached by default. However, Next.js will prerender the route and the output will be cached for improved performance. If you'd like to opt into dynamic rendering, use the { cache: 'no-store' } option. See the fetch API Reference.
During development, you can log fetch calls for better visibility and debugging. See the logging API reference.
With an ORM or database
Since Server Components are rendered on the server, you can safely make database queries using an ORM or database client. Turn your component into an asynchronous function, and await the call:

app/blog/page.tsx
TypeScript

TypeScript

import { db, posts } from '@/lib/db'
 
export default async function Page() {
  const allPosts = await db.select().from(posts)
  return (
    <ul>
      {allPosts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
Client Components
There are two ways to fetch data in Client Components, using:

React's use hook
A community library like SWR or React Query
Streaming data with the use hook
You can use React's use hook to stream data from the server to client. Start by fetching data in your Server component, and pass the promise to your Client Component as prop:

app/blog/page.tsx
TypeScript

TypeScript

import Posts from '@/app/ui/posts'
import { Suspense } from 'react'
 
export default function Page() {
  // Don't await the data fetching function
  const posts = getPosts()
 
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Posts posts={posts} />
    </Suspense>
  )
}
Then, in your Client Component, use the use hook to read the promise:

app/ui/posts.tsx
TypeScript

TypeScript

'use client'
import { use } from 'react'
 
export default function Posts({
  posts,
}: {
  posts: Promise<{ id: string; title: string }[]>
}) {
  const allPosts = use(posts)
 
  return (
    <ul>
      {allPosts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
In the example above, the <Posts> component is wrapped in a <Suspense> boundary. This means the fallback will be shown while the promise is being resolved. Learn more about streaming.

Community libraries
You can use a community library like SWR or React Query to fetch data in Client Components. These libraries have their own semantics for caching, streaming, and other features. For example, with SWR:

app/blog/page.tsx
TypeScript

TypeScript

'use client'
import useSWR from 'swr'
 
const fetcher = (url) => fetch(url).then((r) => r.json())
 
export default function BlogPage() {
  const { data, error, isLoading } = useSWR(
    'https://api.vercel.app/blog',
    fetcher
  )
 
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
 
  return (
    <ul>
      {data.map((post: { id: string; title: string }) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
Deduplicate requests and cache data
One way to deduplicate fetch requests is with request memoization. With this mechanism, fetch calls using GET or HEAD with the same URL and options in a single render pass are combined into one request. This happens automatically, and you can opt out by passing an Abort signal to fetch.

Request memoization is scoped to the lifetime of a request.

You can also deduplicate fetch requests by using Next.js’ Data Cache, for example by setting cache: 'force-cache' in your fetch options.

Data Cache allows sharing data across the current render pass and incoming requests.

If you are not using fetch, and instead using an ORM or database directly, you can wrap your data access with the React cache function.

app/lib/data.ts
TypeScript

TypeScript

import { cache } from 'react'
import { db, posts, eq } from '@/lib/db'
 
export const getPost = cache(async (id: string) => {
  const post = await db.query.posts.findFirst({
    where: eq(posts.id, parseInt(id)),
  })
})
Streaming
Warning: The content below assumes the cacheComponents config option is enabled in your application. The flag was introduced in Next.js 15 canary.

When using async/await in Server Components, Next.js will opt into dynamic rendering. This means the data will be fetched and rendered on the server for every user request. If there are any slow data requests, the whole route will be blocked from rendering.

To improve the initial load time and user experience, you can use streaming to break up the page's HTML into smaller chunks and progressively send those chunks from the server to the client.

How Server Rendering with Streaming Works
There are two ways you can implement streaming in your application:

Wrapping a page with a loading.js file
Wrapping a component with <Suspense>
With loading.js
You can create a loading.js file in the same folder as your page to stream the entire page while the data is being fetched. For example, to stream app/blog/page.js, add the file inside the app/blog folder.

Blog folder structure with loading.js file
app/blog/loading.tsx
TypeScript

TypeScript

export default function Loading() {
  // Define the Loading UI here
  return <div>Loading...</div>
}
On navigation, the user will immediately see the layout and a loading state while the page is being rendered. The new content will then be automatically swapped in once rendering is complete.

Loading UI
Behind-the-scenes, loading.js will be nested inside layout.js, and will automatically wrap the page.js file and any children below in a <Suspense> boundary.

loading.js overview
This approach works well for route segments (layouts and pages), but for more granular streaming, you can use <Suspense>.

With <Suspense>
<Suspense> allows you to be more granular about what parts of the page to stream. For example, you can immediately show any page content that falls outside of the <Suspense> boundary, and stream in the list of blog posts inside the boundary.

app/blog/page.tsx
TypeScript

TypeScript

import { Suspense } from 'react'
import BlogList from '@/components/BlogList'
import BlogListSkeleton from '@/components/BlogListSkeleton'
 
export default function BlogPage() {
  return (
    <div>
      {/* This content will be sent to the client immediately */}
      <header>
        <h1>Welcome to the Blog</h1>
        <p>Read the latest posts below.</p>
      </header>
      <main>
        {/* Any content wrapped in a <Suspense> boundary will be streamed */}
        <Suspense fallback={<BlogListSkeleton />}>
          <BlogList />
        </Suspense>
      </main>
    </div>
  )
}
Creating meaningful loading states
An instant loading state is fallback UI that is shown immediately to the user after navigation. For the best user experience, we recommend designing loading states that are meaningful and help users understand the app is responding. For example, you can use skeletons and spinners, or a small but meaningful part of future screens such as a cover photo, title, etc.

In development, you can preview and inspect the loading state of your components using the React Devtools.

Examples
Sequential data fetching
Sequential data fetching happens when nested components in a tree each fetch their own data and the requests are not deduplicated, leading to longer response times.

Sequential and Parallel Data Fetching
There may be cases where you want this pattern because one fetch depends on the result of the other.

For example, the <Playlists> component will only start fetching data once the <Artist> component has finished fetching data because <Playlists> depends on the artistID prop:

app/artist/[username]/page.tsx
TypeScript

TypeScript

export default async function Page({
  params,
}: {
  params: Promise<{ username: string }>
}) {
  const { username } = await params
  // Get artist information
  const artist = await getArtist(username)
 
  return (
    <>
      <h1>{artist.name}</h1>
      {/* Show fallback UI while the Playlists component is loading */}
      <Suspense fallback={<div>Loading...</div>}>
        {/* Pass the artist ID to the Playlists component */}
        <Playlists artistID={artist.id} />
      </Suspense>
    </>
  )
}
 
async function Playlists({ artistID }: { artistID: string }) {
  // Use the artist ID to fetch playlists
  const playlists = await getArtistPlaylists(artistID)
 
  return (
    <ul>
      {playlists.map((playlist) => (
        <li key={playlist.id}>{playlist.name}</li>
      ))}
    </ul>
  )
}
To improve the user experience, you should use React <Suspense> to show a fallback while data is being fetch. This will enable streaming and prevent the whole route from being blocked by the sequential data requests.

Parallel data fetching
Parallel data fetching happens when data requests in a route are eagerly initiated and start at the same time.

By default, layouts and pages are rendered in parallel. So each segment starts fetching data as soon as possible.

However, within any component, multiple async/await requests can still be sequential if placed after the other. For example, getAlbums will be blocked until getArtist is resolved:

app/artist/[username]/page.tsx
TypeScript

TypeScript

import { getArtist, getAlbums } from '@/app/lib/data'
 
export default async function Page({ params }) {
  // These requests will be sequential
  const { username } = await params
  const artist = await getArtist(username)
  const albums = await getAlbums(username)
  return <div>{artist.name}</div>
}
You can initiate requests in parallel by defining them outside the components that use the data, and resolving them together, for example, with Promise.all:

app/artist/[username]/page.tsx
TypeScript

TypeScript

import Albums from './albums'
 
async function getArtist(username: string) {
  const res = await fetch(`https://api.example.com/artist/${username}`)
  return res.json()
}
 
async function getAlbums(username: string) {
  const res = await fetch(`https://api.example.com/artist/${username}/albums`)
  return res.json()
}
 
export default async function Page({
  params,
}: {
  params: Promise<{ username: string }>
}) {
  const { username } = await params
  const artistData = getArtist(username)
  const albumsData = getAlbums(username)
 
  // Initiate both requests in parallel
  const [artist, albums] = await Promise.all([artistData, albumsData])
 
  return (
    <>
      <h1>{artist.name}</h1>
      <Albums list={albums} />
    </>
  )
}
Good to know: If one request fails when using Promise.all, the entire operation will fail. To handle this, you can use the Promise.allSettled method instead.

Preloading data
You can preload data by creating an utility function that you eagerly call above blocking requests. <Item> conditionally renders based on the checkIsAvailable() function.

You can call preload() before checkIsAvailable() to eagerly initiate <Item/> data dependencies. By the time <Item/> is rendered, its data has already been fetched.

app/item/[id]/page.tsx
TypeScript

TypeScript

import { getItem, checkIsAvailable } from '@/lib/data'
 
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  // starting loading item data
  preload(id)
  // perform another asynchronous task
  const isAvailable = await checkIsAvailable()
 
  return isAvailable ? <Item id={id} /> : null
}
 
export const preload = (id: string) => {
  // void evaluates the given expression and returns undefined
  // https://developer.mozilla.org/docs/Web/JavaScript/Reference/Operators/void
  void getItem(id)
}
export async function Item({ id }: { id: string }) {
  const result = await getItem(id)
  // ...
}
Additionally, you can use React's cache function and the server-only package to create a reusable utility function. This approach allows you to cache the data fetching function and ensure that it's only executed on the server.

utils/get-item.ts
TypeScript

TypeScript

import { cache } from 'react'
import 'server-only'
import { getItem } from '@/lib/data'
 
export const preload = (id: string) => {
  void getItem(id)
}
 
export const getItem = cache(async (id: string) => {
  // ...
})
API Reference
Learn more about the features mentioned in this page by reading the API Reference.
Data Security
Learn the built-in data security features in Next.js and learn best practices for protecting your application's data.
fetch
API reference for the extended fetch function.
loading.js
API reference for the loading.js file.
logging
Configure how data fetches are logged to the console when running Next.js in development mode.
taint
Enable tainting Objects and Values.
Previous
Partial Prerendering
Next
Updating Data
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Getting Started: Fetching Data | Next.js


Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
API Reference
Directives
Components
File-system conventions
Functions
Configuration
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
When to use Server and Client Components?
How do Server and Client Components work in Next.js?
On the server
On the client (first load)
Subsequent Navigations
Examples
Using Client Components
Reducing JS bundle size
Passing data from Server to Client Components
Interleaving Server and Client Components
Context providers
Third-party components
Preventing environment poisoning
Next Steps
Edit this page on GitHub
Scroll to top
App Router
Getting Started
Server and Client Components
Server and Client Components
By default, layouts and pages are Server Components, which lets you fetch data and render parts of your UI on the server, optionally cache the result, and stream it to the client. When you need interactivity or browser APIs, you can use Client Components to layer in functionality.

This page explains how Server and Client Components work in Next.js and when to use them, with examples of how to compose them together in your application.

When to use Server and Client Components?
The client and server environments have different capabilities. Server and Client components allow you to run logic in each environment depending on your use case.

Use Client Components when you need:

State and event handlers. E.g. onClick, onChange.
Lifecycle logic. E.g. useEffect.
Browser-only APIs. E.g. localStorage, window, Navigator.geolocation, etc.
Custom hooks.
Use Server Components when you need:

Fetch data from databases or APIs close to the source.
Use API keys, tokens, and other secrets without exposing them to the client.
Reduce the amount of JavaScript sent to the browser.
Improve the First Contentful Paint (FCP), and stream content progressively to the client.
For example, the <Page> component is a Server Component that fetches data about a post, and passes it as props to the <LikeButton> which handles client-side interactivity.

app/[id]/page.tsx
TypeScript

TypeScript

import LikeButton from '@/app/ui/like-button'
import { getPost } from '@/lib/data'
 
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const post = await getPost(id)
 
  return (
    <div>
      <main>
        <h1>{post.title}</h1>
        {/* ... */}
        <LikeButton likes={post.likes} />
      </main>
    </div>
  )
}
app/ui/like-button.tsx
TypeScript

TypeScript

'use client'
 
import { useState } from 'react'
 
export default function LikeButton({ likes }: { likes: number }) {
  // ...
}
How do Server and Client Components work in Next.js?
On the server
On the server, Next.js uses React's APIs to orchestrate rendering. The rendering work is split into chunks, by individual route segments (layouts and pages):

Server Components are rendered into a special data format called the React Server Component Payload (RSC Payload).
Client Components and the RSC Payload are used to prerender HTML.
What is the React Server Component Payload (RSC)?

The RSC Payload is a compact binary representation of the rendered React Server Components tree. It's used by React on the client to update the browser's DOM. The RSC Payload contains:

The rendered result of Server Components
Placeholders for where Client Components should be rendered and references to their JavaScript files
Any props passed from a Server Component to a Client Component
On the client (first load)
Then, on the client:

HTML is used to immediately show a fast non-interactive preview of the route to the user.
RSC Payload is used to reconcile the Client and Server Component trees.
JavaScript is used to hydrate Client Components and make the application interactive.
What is hydration?

Hydration is React's process for attaching event handlers to the DOM, to make the static HTML interactive.

Subsequent Navigations
On subsequent navigations:

The RSC Payload is prefetched and cached for instant navigation.
Client Components are rendered entirely on the client, without the server-rendered HTML.
Examples
Using Client Components
You can create a Client Component by adding the "use client" directive at the top of the file, above your imports.

app/ui/counter.tsx
TypeScript

TypeScript

'use client'
 
import { useState } from 'react'
 
export default function Counter() {
  const [count, setCount] = useState(0)
 
  return (
    <div>
      <p>{count} likes</p>
      <button onClick={() => setCount(count + 1)}>Click me</button>
    </div>
  )
}
"use client" is used to declare a boundary between the Server and Client module graphs (trees).

Once a file is marked with "use client", all its imports and child components are considered part of the client bundle. This means you don't need to add the directive to every component that is intended for the client.

Reducing JS bundle size
To reduce the size of your client JavaScript bundles, add 'use client' to specific interactive components instead of marking large parts of your UI as Client Components.

For example, the <Layout> component contains mostly static elements like a logo and navigation links, but includes an interactive search bar. <Search /> is interactive and needs to be a Client Component, however, the rest of the layout can remain a Server Component.

app/layout.tsx
TypeScript

TypeScript

// Client Component
import Search from './search'
// Server Component
import Logo from './logo'
 
// Layout is a Server Component by default
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <nav>
        <Logo />
        <Search />
      </nav>
      <main>{children}</main>
    </>
  )
}
app/ui/search.tsx
TypeScript

TypeScript

'use client'
 
export default function Search() {
  // ...
}
Passing data from Server to Client Components
You can pass data from Server Components to Client Components using props.

app/[id]/page.tsx
TypeScript

TypeScript

import LikeButton from '@/app/ui/like-button'
import { getPost } from '@/lib/data'
 
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const post = await getPost(id)
 
  return <LikeButton likes={post.likes} />
}
app/ui/like-button.tsx
TypeScript

TypeScript

'use client'
 
export default function LikeButton({ likes }: { likes: number }) {
  // ...
}
Alternatively, you can stream data from a Server Component to a Client Component with the use Hook. See an example.

Good to know: Props passed to Client Components need to be serializable by React.

Interleaving Server and Client Components
You can pass Server Components as a prop to a Client Component. This allows you to visually nest server-rendered UI within Client components.

A common pattern is to use children to create a slot in a <ClientComponent>. For example, a <Cart> component that fetches data on the server, inside a <Modal> component that uses client state to toggle visibility.

app/ui/modal.tsx
TypeScript

TypeScript

'use client'
 
export default function Modal({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}
Then, in a parent Server Component (e.g.<Page>), you can pass a <Cart> as the child of the <Modal>:

app/page.tsx
TypeScript

TypeScript

import Modal from './ui/modal'
import Cart from './ui/cart'
 
export default function Page() {
  return (
    <Modal>
      <Cart />
    </Modal>
  )
}
In this pattern, all Server Components will be rendered on the server ahead of time, including those as props. The resulting RSC payload will contain references of where Client Components should be rendered within the component tree.

Context providers
React context is commonly used to share global state like the current theme. However, React context is not supported in Server Components.

To use context, create a Client Component that accepts children:

app/theme-provider.tsx
TypeScript

TypeScript

'use client'
 
import { createContext } from 'react'
 
export const ThemeContext = createContext({})
 
export default function ThemeProvider({
  children,
}: {
  children: React.ReactNode
}) {
  return <ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>
}
Then, import it into a Server Component (e.g. layout):

app/layout.tsx
TypeScript

TypeScript

import ThemeProvider from './theme-provider'
 
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
Your Server Component will now be able to directly render your provider, and all other Client Components throughout your app will be able to consume this context.

Good to know: You should render providers as deep as possible in the tree – notice how ThemeProvider only wraps {children} instead of the entire <html> document. This makes it easier for Next.js to optimize the static parts of your Server Components.

Third-party components
When using a third-party component that relies on client-only features, you can wrap it in a Client Component to ensure it works as expected.

For example, the <Carousel /> can be imported from the acme-carousel package. This component uses useState, but it doesn't yet have the "use client" directive.

If you use <Carousel /> within a Client Component, it will work as expected:

app/gallery.tsx
TypeScript

TypeScript

'use client'
 
import { useState } from 'react'
import { Carousel } from 'acme-carousel'
 
export default function Gallery() {
  const [isOpen, setIsOpen] = useState(false)
 
  return (
    <div>
      <button onClick={() => setIsOpen(true)}>View pictures</button>
      {/* Works, since Carousel is used within a Client Component */}
      {isOpen && <Carousel />}
    </div>
  )
}
However, if you try to use it directly within a Server Component, you'll see an error. This is because Next.js doesn't know <Carousel /> is using client-only features.

To fix this, you can wrap third-party components that rely on client-only features in your own Client Components:

app/carousel.tsx
TypeScript

TypeScript

'use client'
 
import { Carousel } from 'acme-carousel'
 
export default Carousel
Now, you can use <Carousel /> directly within a Server Component:

app/page.tsx
TypeScript

TypeScript

import Carousel from './carousel'
 
export default function Page() {
  return (
    <div>
      <p>View pictures</p>
      {/*  Works, since Carousel is a Client Component */}
      <Carousel />
    </div>
  )
}
Advice for Library Authors

If you’re building a component library, add the "use client" directive to entry points that rely on client-only features. This lets your users import components into Server Components without needing to create wrappers.

It's worth noting some bundlers might strip out "use client" directives. You can find an example of how to configure esbuild to include the "use client" directive in the React Wrap Balancer and Vercel Analytics repositories.

Preventing environment poisoning
JavaScript modules can be shared between both Server and Client Components modules. This means it's possible to accidentally import server-only code into the client. For example, consider the following function:

lib/data.ts
TypeScript

TypeScript

export async function getData() {
  const res = await fetch('https://external-service.com/data', {
    headers: {
      authorization: process.env.API_KEY,
    },
  })
 
  return res.json()
}
This function contains an API_KEY that should never be exposed to the client.

In Next.js, only environment variables prefixed with NEXT_PUBLIC_ are included in the client bundle. If variables are not prefixed, Next.js replaces them with an empty string.

As a result, even though getData() can be imported and executed on the client, it won't work as expected.

To prevent accidental usage in Client Components, you can use the server-only package.

Then, import the package into a file that contains server-only code:

lib/data.js

import 'server-only'
 
export async function getData() {
  const res = await fetch('https://external-service.com/data', {
    headers: {
      authorization: process.env.API_KEY,
    },
  })
 
  return res.json()
}
Now, if you try to import the module into a Client Component, there will be a build-time error.

The corresponding client-only package can be used to mark modules that contain client-only logic like code that accesses the window object.

In Next.js, installing server-only or client-only is optional. However, if your linting rules flag extraneous dependencies, you may install them to avoid issues.

pnpm
npm
yarn
bun
Terminal

pnpm add server-only
Next.js handles server-only and client-only imports internally to provide clearer error messages when a module is used in the wrong environment. The contents of these packages from NPM are not used by Next.js.

Next.js also provides its own type declarations for server-only and client-only, for TypeScript configurations where noUncheckedSideEffectImports is active.

Next Steps
Learn more about the APIs mentioned in this page.
use client
Learn how to use the use client directive to render a component on the client.
Previous
Linking and Navigating
Next
Partial Prerendering
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Getting Started: Server and Client Components | Next.js
Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
API Reference
Directives
Components
Font
Form Component
Image Component
Link Component
Script Component
File-system conventions
default.js
Dynamic Segments
error.js
forbidden.js
instrumentation.js
instrumentation-client.js
Intercepting Routes
layout.js
loading.js
mdx-components.js
middleware.js
not-found.js
page.js
Parallel Routes
public
route.js
Route Groups
Route Segment Config
src
template.js
unauthorized.js
Metadata Files
Functions
Configuration
next.config.js
TypeScript
ESLint
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
Folder and file conventions
Top-level folders
Top-level files
Routing Files
Nested routes
Dynamic routes
Route Groups and private folders
Parallel and Intercepted Routes
Metadata file conventions
App icons
Open Graph and Twitter images
SEO
Organizing your project
Component hierarchy
Colocation
Private folders
Route groups
src folder
Examples
Store project files outside of app
Store project files in top-level folders inside of app
Split project files by feature or route
Organize routes without affecting the URL path
Opting specific segments into a layout
Opting for loading skeletons on a specific route
Creating multiple root layouts
Edit this page on GitHub
Scroll to top
App Router
Getting Started
Project Structure
Project structure and organization
This page provides an overview of all the folder and file conventions in Next.js, and recommendations for organizing your project.

Folder and file conventions
Top-level folders
Top-level folders are used to organize your application's code and static assets.

Route segments to path segments
app	App Router
pages	Pages Router
public	Static assets to be served
src	Optional application source folder
Top-level files
Top-level files are used to configure your application, manage dependencies, run middleware, integrate monitoring tools, and define environment variables.

Next.js	
next.config.js	Configuration file for Next.js
package.json	Project dependencies and scripts
instrumentation.ts	OpenTelemetry and Instrumentation file
middleware.ts	Next.js request middleware
.env	Environment variables
.env.local	Local environment variables
.env.production	Production environment variables
.env.development	Development environment variables
.eslintrc.json	Configuration file for ESLint
.gitignore	Git files and folders to ignore
next-env.d.ts	TypeScript declaration file for Next.js
tsconfig.json	Configuration file for TypeScript
jsconfig.json	Configuration file for JavaScript
Routing Files
layout	.js .jsx .tsx	Layout
page	.js .jsx .tsx	Page
loading	.js .jsx .tsx	Loading UI
not-found	.js .jsx .tsx	Not found UI
error	.js .jsx .tsx	Error UI
global-error	.js .jsx .tsx	Global error UI
route	.js .ts	API endpoint
template	.js .jsx .tsx	Re-rendered layout
default	.js .jsx .tsx	Parallel route fallback page
Nested routes
folder	Route segment
folder/folder	Nested route segment
Dynamic routes
[folder]	Dynamic route segment
[...folder]	Catch-all route segment
[[...folder]]	Optional catch-all route segment
Route Groups and private folders
(folder)	Group routes without affecting routing
_folder	Opt folder and all child segments out of routing
Parallel and Intercepted Routes
@folder	Named slot
(.)folder	Intercept same level
(..)folder	Intercept one level above
(..)(..)folder	Intercept two levels above
(...)folder	Intercept from root
Metadata file conventions
App icons
favicon	.ico	Favicon file
icon	.ico .jpg .jpeg .png .svg	App Icon file
icon	.js .ts .tsx	Generated App Icon
apple-icon	.jpg .jpeg, .png	Apple App Icon file
apple-icon	.js .ts .tsx	Generated Apple App Icon
Open Graph and Twitter images
opengraph-image	.jpg .jpeg .png .gif	Open Graph image file
opengraph-image	.js .ts .tsx	Generated Open Graph image
twitter-image	.jpg .jpeg .png .gif	Twitter image file
twitter-image	.js .ts .tsx	Generated Twitter image
SEO
sitemap	.xml	Sitemap file
sitemap	.js .ts	Generated Sitemap
robots	.txt	Robots file
robots	.js .ts	Generated Robots file
Organizing your project
Next.js is unopinionated about how you organize and colocate your project files. But it does provide several features to help you organize your project.

Component hierarchy
The components defined in special files are rendered in a specific hierarchy:

layout.js
template.js
error.js (React error boundary)
loading.js (React suspense boundary)
not-found.js (React error boundary)
page.js or nested layout.js
Component Hierarchy for File Conventions
The components are rendered recursively in nested routes, meaning the components of a route segment will be nested inside the components of its parent segment.

Nested File Conventions Component Hierarchy
Colocation
In the app directory, nested folders define route structure. Each folder represents a route segment that is mapped to a corresponding segment in a URL path.

However, even though route structure is defined through folders, a route is not publicly accessible until a page.js or route.js file is added to a route segment.

A diagram showing how a route is not publicly accessible until a page.js or route.js file is added to a route segment.
And, even when a route is made publicly accessible, only the content returned by page.js or route.js is sent to the client.

A diagram showing how page.js and route.js files make routes publicly accessible.
This means that project files can be safely colocated inside route segments in the app directory without accidentally being routable.

A diagram showing colocated project files are not routable even when a segment contains a page.js or route.js file.
Good to know: While you can colocate your project files in app you don't have to. If you prefer, you can keep them outside the app directory.

Private folders
Private folders can be created by prefixing a folder with an underscore: _folderName

This indicates the folder is a private implementation detail and should not be considered by the routing system, thereby opting the folder and all its subfolders out of routing.

An example folder structure using private folders
Since files in the app directory can be safely colocated by default, private folders are not required for colocation. However, they can be useful for:

Separating UI logic from routing logic.
Consistently organizing internal files across a project and the Next.js ecosystem.
Sorting and grouping files in code editors.
Avoiding potential naming conflicts with future Next.js file conventions.
Good to know:

While not a framework convention, you might also consider marking files outside private folders as "private" using the same underscore pattern.
You can create URL segments that start with an underscore by prefixing the folder name with %5F (the URL-encoded form of an underscore): %5FfolderName.
If you don't use private folders, it would be helpful to know Next.js special file conventions to prevent unexpected naming conflicts.
Route groups
Route groups can be created by wrapping a folder in parenthesis: (folderName)

This indicates the folder is for organizational purposes and should not be included in the route's URL path.

An example folder structure using route groups
Route groups are useful for:

Organizing routes by site section, intent, or team. e.g. marketing pages, admin pages, etc.
Enabling nested layouts in the same route segment level:
Creating multiple nested layouts in the same segment, including multiple root layouts
Adding a layout to a subset of routes in a common segment
src folder
Next.js supports storing application code (including app) inside an optional src folder. This separates application code from project configuration files which mostly live in the root of a project.

An example folder structure with the `src` folder
Examples
The following section lists a very high-level overview of common strategies. The simplest takeaway is to choose a strategy that works for you and your team and be consistent across the project.

Good to know: In our examples below, we're using components and lib folders as generalized placeholders, their naming has no special framework significance and your projects might use other folders like ui, utils, hooks, styles, etc.

Store project files outside of app
This strategy stores all application code in shared folders in the root of your project and keeps the app directory purely for routing purposes.

An example folder structure with project files outside of app
Store project files in top-level folders inside of app
This strategy stores all application code in shared folders in the root of the app directory.

An example folder structure with project files inside app
Split project files by feature or route
This strategy stores globally shared application code in the root app directory and splits more specific application code into the route segments that use them.

An example folder structure with project files split by feature or route
Organize routes without affecting the URL path
To organize routes without affecting the URL, create a group to keep related routes together. The folders in parenthesis will be omitted from the URL (e.g. (marketing) or (shop)).

Organizing Routes with Route Groups
Even though routes inside (marketing) and (shop) share the same URL hierarchy, you can create a different layout for each group by adding a layout.js file inside their folders.

Route Groups with Multiple Layouts
Opting specific segments into a layout
To opt specific routes into a layout, create a new route group (e.g. (shop)) and move the routes that share the same layout into the group (e.g. account and cart). The routes outside of the group will not share the layout (e.g. checkout).

Route Groups with Opt-in Layouts
Opting for loading skeletons on a specific route
To apply a loading skeleton via a loading.js file to a specific route, create a new route group (e.g., /(overview)) and then move your loading.tsx inside that route group.

Folder structure showing a loading.tsx and a page.tsx inside the route group
Now, the loading.tsx file will only apply to your dashboard → overview page instead of all your dashboard pages without affecting the URL path structure.

Creating multiple root layouts
To create multiple root layouts, remove the top-level layout.js file, and add a layout.js file inside each route group. This is useful for partitioning an application into sections that have a completely different UI or experience. The <html> and <body> tags need to be added to each root layout.

Route Groups with Multiple Root Layouts
In the example above, both (marketing) and (shop) have their own root layout.

Previous
Installation
Next
Layouts and Pages
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Getting Started: Project Structure | Next.js


How to set up Jest with Next.js
Jest and React Testing Library are frequently used together for Unit Testing and Snapshot Testing. This guide will show you how to set up Jest with Next.js and write your first tests.

Good to know: Since async Server Components are new to the React ecosystem, Jest currently does not support them. While you can still run unit tests for synchronous Server and Client Components, we recommend using an E2E tests for async components.

Quickstart
You can use create-next-app with the Next.js with-jest example to quickly get started:

Terminal

npx create-next-app@latest --example with-jest with-jest-app
Manual setup
Since the release of Next.js 12, Next.js now has built-in configuration for Jest.

To set up Jest, install jest and the following packages as dev dependencies:

Terminal

npm install -D jest jest-environment-jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom ts-node @types/jest
# or
yarn add -D jest jest-environment-jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom ts-node @types/jest
# or
pnpm install -D jest jest-environment-jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom ts-node @types/jest
Generate a basic Jest configuration file by running the following command:

Terminal

npm init jest@latest
# or
yarn create jest@latest
# or
pnpm create jest@latest
This will take you through a series of prompts to setup Jest for your project, including automatically creating a jest.config.ts|js file.

Update your config file to use next/jest. This transformer has all the necessary configuration options for Jest to work with Next.js:

jest.config.ts
TypeScript

TypeScript

import type { Config } from 'jest'
import nextJest from 'next/jest.js'
 
const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})
 
// Add any custom config to be passed to Jest
const config: Config = {
  coverageProvider: 'v8',
  testEnvironment: 'jsdom',
  // Add more setup options before each test is run
  // setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
}
 
// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
export default createJestConfig(config)
Under the hood, next/jest is automatically configuring Jest for you, including:

Setting up transform using the Next.js Compiler.
Auto mocking stylesheets (.css, .module.css, and their scss variants), image imports and next/font.
Loading .env (and all variants) into process.env.
Ignoring node_modules from test resolving and transforms.
Ignoring .next from test resolving.
Loading next.config.js for flags that enable SWC transforms.
Good to know: To test environment variables directly, load them manually in a separate setup script or in your jest.config.ts file. For more information, please see Test Environment Variables.

Optional: Handling Absolute Imports and Module Path Aliases
If your project is using Module Path Aliases, you will need to configure Jest to resolve the imports by matching the paths option in the jsconfig.json file with the moduleNameMapper option in the jest.config.js file. For example:

tsconfig.json or jsconfig.json

{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler",
    "baseUrl": "./",
    "paths": {
      "@/components/*": ["components/*"]
    }
  }
}
jest.config.js

moduleNameMapper: {
  // ...
  '^@/components/(.*)$': '<rootDir>/components/$1',
}
Optional: Extend Jest with custom matchers
@testing-library/jest-dom includes a set of convenient custom matchers such as .toBeInTheDocument() making it easier to write tests. You can import the custom matchers for every test by adding the following option to the Jest configuration file:

jest.config.ts
TypeScript

TypeScript

setupFilesAfterEnv: ['<rootDir>/jest.setup.ts']
Then, inside jest.setup, add the following import:

jest.setup.ts
TypeScript

TypeScript

import '@testing-library/jest-dom'
Good to know: extend-expect was removed in v6.0, so if you are using @testing-library/jest-dom before version 6, you will need to import @testing-library/jest-dom/extend-expect instead.

If you need to add more setup options before each test, you can add them to the jest.setup file above.

Add a test script to package.json
Finally, add a Jest test script to your package.json file:

package.json

{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "jest",
    "test:watch": "jest --watch"
  }
}
jest --watch will re-run tests when a file is changed. For more Jest CLI options, please refer to the Jest Docs.

Creating your first test
Your project is now ready to run tests. Create a folder called __tests__ in your project's root directory.

For example, we can add a test to check if the <Page /> component successfully renders a heading:

app/page.js

import Link from 'next/link'
 
export default function Page() {
  return (
    <div>
      <h1>Home</h1>
      <Link href="/about">About</Link>
    </div>
  )
}
__tests__/page.test.jsx

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Page from '../app/page'
 
describe('Page', () => {
  it('renders a heading', () => {
    render(<Page />)
 
    const heading = screen.getByRole('heading', { level: 1 })
 
    expect(heading).toBeInTheDocument()
  })
})
Optionally, add a snapshot test to keep track of any unexpected changes in your component:

__tests__/snapshot.js

import { render } from '@testing-library/react'
import Page from '../app/page'
 
it('renders homepage unchanged', () => {
  const { container } = render(<Page />)
  expect(container).toMatchSnapshot()
})
Running your tests
Then, run the following command to run your tests:

Terminal

npm run test
# or
yarn test
# or
pnpm test
Additional Resources
For further reading, you may find these resources helpful:

Next.js with Jest example
Jest Docs
React Testing Library Docs
Testing Playground - use good testing practices to match elements.
Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
Analytics
Authentication
Backend for Frontend
Caching
CI Build Caching
Content Security Policy
CSS-in-JS
Custom Server
Data Security
Debugging
Draft Mode
Environment Variables
Forms
ISR
Instrumentation
Internationalization
JSON-LD
Lazy Loading
Development Environment
MDX
Memory Usage
Migrating
Multi-tenant
Multi-zones
OpenTelemetry
Package Bundling
Prefetching
Production
PWAs
Redirecting
Sass
Scripts
Self-Hosting
SPAs
Static Exports
Tailwind CSS v3
Testing
Cypress
Jest
Playwright
Vitest
Third Party Libraries
Upgrading
Codemods
Version 14
Version 15
Videos
API Reference
Directives
Components
Font
Form Component
Image Component
Link Component
Script Component
File-system conventions
default.js
Dynamic Segments
error.js
forbidden.js
instrumentation.js
instrumentation-client.js
Intercepting Routes
layout.js
loading.js
mdx-components.js
middleware.js
not-found.js
page.js
Parallel Routes
public
route.js
Route Groups
Route Segment Config
src
template.js
unauthorized.js
Metadata Files
Functions
Configuration
next.config.js
TypeScript
ESLint
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
Creating a PWA with Next.js
1. Creating the Web App Manifest
2. Implementing Web Push Notifications
3. Implementing Server Actions
4. Generating VAPID Keys
5. Creating a Service Worker
6. Adding to Home Screen
7. Testing Locally
8. Securing your application
Extending your PWA
Next Steps
Edit this page on GitHub
Scroll to top
App Router
Guides
PWAs
How to build a Progressive Web Application (PWA) with Next.js
Progressive Web Applications (PWAs) offer the reach and accessibility of web applications combined with the features and user experience of native mobile apps. With Next.js, you can create PWAs that provide a seamless, app-like experience across all platforms without the need for multiple codebases or app store approvals.

PWAs allow you to:

Deploy updates instantly without waiting for app store approval
Create cross-platform applications with a single codebase
Provide native-like features such as home screen installation and push notifications
Creating a PWA with Next.js
1. Creating the Web App Manifest
Next.js provides built-in support for creating a web app manifest using the App Router. You can create either a static or dynamic manifest file:

For example, create a app/manifest.ts or app/manifest.json file:

app/manifest.ts
TypeScript

TypeScript

import type { MetadataRoute } from 'next'
 
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Next.js PWA',
    short_name: 'NextPWA',
    description: 'A Progressive Web App built with Next.js',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#000000',
    icons: [
      {
        src: '/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  }
}
This file should contain information about the name, icons, and how it should be displayed as an icon on the user's device. This will allow users to install your PWA on their home screen, providing a native app-like experience.

You can use tools like favicon generators to create the different icon sets and place the generated files in your public/ folder.

2. Implementing Web Push Notifications
Web Push Notifications are supported with all modern browsers, including:

iOS 16.4+ for applications installed to the home screen
Safari 16 for macOS 13 or later
Chromium based browsers
Firefox
This makes PWAs a viable alternative to native apps. Notably, you can trigger install prompts without needing offline support.

Web Push Notifications allow you to re-engage users even when they're not actively using your app. Here's how to implement them in a Next.js application:

First, let's create the main page component in app/page.tsx. We'll break it down into smaller parts for better understanding. First, we’ll add some of the imports and utilities we’ll need. It’s okay that the referenced Server Actions do not yet exist:


'use client'
 
import { useState, useEffect } from 'react'
import { subscribeUser, unsubscribeUser, sendNotification } from './actions'
 
function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
 
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
 
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}
Let’s now add a component to manage subscribing, unsubscribing, and sending push notifications.


function PushNotificationManager() {
  const [isSupported, setIsSupported] = useState(false)
  const [subscription, setSubscription] = useState<PushSubscription | null>(
    null
  )
  const [message, setMessage] = useState('')
 
  useEffect(() => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      setIsSupported(true)
      registerServiceWorker()
    }
  }, [])
 
  async function registerServiceWorker() {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
      updateViaCache: 'none',
    })
    const sub = await registration.pushManager.getSubscription()
    setSubscription(sub)
  }
 
  async function subscribeToPush() {
    const registration = await navigator.serviceWorker.ready
    const sub = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!
      ),
    })
    setSubscription(sub)
    const serializedSub = JSON.parse(JSON.stringify(sub))
    await subscribeUser(serializedSub)
  }
 
  async function unsubscribeFromPush() {
    await subscription?.unsubscribe()
    setSubscription(null)
    await unsubscribeUser()
  }
 
  async function sendTestNotification() {
    if (subscription) {
      await sendNotification(message)
      setMessage('')
    }
  }
 
  if (!isSupported) {
    return <p>Push notifications are not supported in this browser.</p>
  }
 
  return (
    <div>
      <h3>Push Notifications</h3>
      {subscription ? (
        <>
          <p>You are subscribed to push notifications.</p>
          <button onClick={unsubscribeFromPush}>Unsubscribe</button>
          <input
            type="text"
            placeholder="Enter notification message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button onClick={sendTestNotification}>Send Test</button>
        </>
      ) : (
        <>
          <p>You are not subscribed to push notifications.</p>
          <button onClick={subscribeToPush}>Subscribe</button>
        </>
      )}
    </div>
  )
}
Finally, let’s create a component to show a message for iOS devices to instruct them to install to their home screen, and only show this if the app is not already installed.


function InstallPrompt() {
  const [isIOS, setIsIOS] = useState(false)
  const [isStandalone, setIsStandalone] = useState(false)
 
  useEffect(() => {
    setIsIOS(
      /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream
    )
 
    setIsStandalone(window.matchMedia('(display-mode: standalone)').matches)
  }, [])
 
  if (isStandalone) {
    return null // Don't show install button if already installed
  }
 
  return (
    <div>
      <h3>Install App</h3>
      <button>Add to Home Screen</button>
      {isIOS && (
        <p>
          To install this app on your iOS device, tap the share button
          <span role="img" aria-label="share icon">
            {' '}
            ⎋{' '}
          </span>
          and then "Add to Home Screen"
          <span role="img" aria-label="plus icon">
            {' '}
            ➕{' '}
          </span>.
        </p>
      )}
    </div>
  )
}
 
export default function Page() {
  return (
    <div>
      <PushNotificationManager />
      <InstallPrompt />
    </div>
  )
}
Now, let’s create the Server Actions which this file calls.

3. Implementing Server Actions
Create a new file to contain your actions at app/actions.ts. This file will handle creating subscriptions, deleting subscriptions, and sending notifications.

app/actions.ts
TypeScript

TypeScript

'use server'
 
import webpush from 'web-push'
 
webpush.setVapidDetails(
  '<mailto:your-email@example.com>',
  process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!,
  process.env.VAPID_PRIVATE_KEY!
)
 
let subscription: PushSubscription | null = null
 
export async function subscribeUser(sub: PushSubscription) {
  subscription = sub
  // In a production environment, you would want to store the subscription in a database
  // For example: await db.subscriptions.create({ data: sub })
  return { success: true }
}
 
export async function unsubscribeUser() {
  subscription = null
  // In a production environment, you would want to remove the subscription from the database
  // For example: await db.subscriptions.delete({ where: { ... } })
  return { success: true }
}
 
export async function sendNotification(message: string) {
  if (!subscription) {
    throw new Error('No subscription available')
  }
 
  try {
    await webpush.sendNotification(
      subscription,
      JSON.stringify({
        title: 'Test Notification',
        body: message,
        icon: '/icon.png',
      })
    )
    return { success: true }
  } catch (error) {
    console.error('Error sending push notification:', error)
    return { success: false, error: 'Failed to send notification' }
  }
}
Sending a notification will be handled by our service worker, created in step 5.

In a production environment, you would want to store the subscription in a database for persistence across server restarts and to manage multiple users' subscriptions.

4. Generating VAPID Keys
To use the Web Push API, you need to generate VAPID keys. The simplest way is to use the web-push CLI directly:

First, install web-push globally:

Terminal

npm install -g web-push
Generate the VAPID keys by running:

Terminal

web-push generate-vapid-keys
Copy the output and paste the keys into your .env file:


NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here
5. Creating a Service Worker
Create a public/sw.js file for your service worker:

public/sw.js

self.addEventListener('push', function (event) {
  if (event.data) {
    const data = event.data.json()
    const options = {
      body: data.body,
      icon: data.icon || '/icon.png',
      badge: '/badge.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: '2',
      },
    }
    event.waitUntil(self.registration.showNotification(data.title, options))
  }
})
 
self.addEventListener('notificationclick', function (event) {
  console.log('Notification click received.')
  event.notification.close()
  event.waitUntil(clients.openWindow('<https://your-website.com>'))
})
This service worker supports custom images and notifications. It handles incoming push events and notification clicks.

You can set custom icons for notifications using the icon and badge properties.
The vibrate pattern can be adjusted to create custom vibration alerts on supported devices.
Additional data can be attached to the notification using the data property.
Remember to test your service worker thoroughly to ensure it behaves as expected across different devices and browsers. Also, make sure to update the 'https://your-website.com' link in the notificationclick event listener to the appropriate URL for your application.

6. Adding to Home Screen
The InstallPrompt component defined in step 2 shows a message for iOS devices to instruct them to install to their home screen.

To ensure your application can be installed to a mobile home screen, you must have:

A valid web app manifest (created in step 1)
The website served over HTTPS
Modern browsers will automatically show an installation prompt to users when these criteria are met. You can provide a custom installation button with beforeinstallprompt, however, we do not recommend this as it is not cross browser and platform (does not work on Safari iOS).

7. Testing Locally
To ensure you can view notifications locally, ensure that:

You are running locally with HTTPS
Use next dev --experimental-https for testing
Your browser (Chrome, Safari, Firefox) has notifications enabled
When prompted locally, accept permissions to use notifications
Ensure notifications are not disabled globally for the entire browser
If you are still not seeing notifications, try using another browser to debug
8. Securing your application
Security is a crucial aspect of any web application, especially for PWAs. Next.js allows you to configure security headers using the next.config.js file. For example:

next.config.js

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
      {
        source: '/sw.js',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/javascript; charset=utf-8',
          },
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self'",
          },
        ],
      },
    ]
  },
}
Let’s go over each of these options:

Global Headers (applied to all routes):
X-Content-Type-Options: nosniff: Prevents MIME type sniffing, reducing the risk of malicious file uploads.
X-Frame-Options: DENY: Protects against clickjacking attacks by preventing your site from being embedded in iframes.
Referrer-Policy: strict-origin-when-cross-origin: Controls how much referrer information is included with requests, balancing security and functionality.
Service Worker Specific Headers:
Content-Type: application/javascript; charset=utf-8: Ensures the service worker is interpreted correctly as JavaScript.
Cache-Control: no-cache, no-store, must-revalidate: Prevents caching of the service worker, ensuring users always get the latest version.
Content-Security-Policy: default-src 'self'; script-src 'self': Implements a strict Content Security Policy for the service worker, only allowing scripts from the same origin.
Learn more about defining Content Security Policies with Next.js.

Extending your PWA
Exploring PWA Capabilities: PWAs can leverage various web APIs to provide advanced functionality. Consider exploring features like background sync, periodic background sync, or the File System Access API to enhance your application. For inspiration and up-to-date information on PWA capabilities, you can refer to resources like What PWA Can Do Today.
Static Exports: If your application requires not running a server, and instead using a static export of files, you can update the Next.js configuration to enable this change. Learn more in the Next.js Static Export documentation. However, you will need to move from Server Actions to calling an external API, as well as moving your defined headers to your proxy.
Offline Support: To provide offline functionality, one option is Serwist with Next.js. You can find an example of how to integrate Serwist with Next.js in their documentation. Note: this plugin currently requires webpack configuration.
Security Considerations: Ensure that your service worker is properly secured. This includes using HTTPS, validating the source of push messages, and implementing proper error handling.
User Experience: Consider implementing progressive enhancement techniques to ensure your app works well even when certain PWA features are not supported by the user's browser.
Next Steps
manifest.json
API Reference for manifest.json file.
Previous
Production
Next
Redirecting
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Guides: PWAs | Next.js

Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
Analytics
Authentication
Backend for Frontend
Caching
CI Build Caching
Content Security Policy
CSS-in-JS
Custom Server
Data Security
Debugging
Draft Mode
Environment Variables
Forms
ISR
Instrumentation
Internationalization
JSON-LD
Lazy Loading
Development Environment
MDX
Memory Usage
Migrating
Multi-tenant
Multi-zones
OpenTelemetry
Package Bundling
Prefetching
Production
PWAs
Redirecting
Sass
Scripts
Self-Hosting
SPAs
Static Exports
Tailwind CSS v3
Testing
Cypress
Jest
Playwright
Vitest
Third Party Libraries
Upgrading
Codemods
Version 14
Version 15
Videos
API Reference
Directives
Components
Font
Form Component
Image Component
Link Component
Script Component
File-system conventions
default.js
Dynamic Segments
error.js
forbidden.js
instrumentation.js
instrumentation-client.js
Intercepting Routes
layout.js
loading.js
mdx-components.js
middleware.js
not-found.js
page.js
Parallel Routes
public
route.js
Route Groups
Route Segment Config
src
template.js
unauthorized.js
Metadata Files
Functions
Configuration
next.config.js
TypeScript
ESLint
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
How does prefetching work?
Prefetching static vs. dynamic routes
Automatic prefetch
Manual prefetch
Hover-triggered prefetch
Extending or ejecting link
Disabled prefetch
Prefetching optimizations
Client cache
Prefetch scheduling
Partial Prerendering (PPR)
Troubleshooting
Triggering unwanted side-effects during prefetching
Preventing too many prefetches
Edit this page on GitHub
Scroll to top
App Router
Guides
Prefetching
Prefetching
Prefetching makes navigating between different routes in your application feel instant. Next.js tries to intelligently prefetch by default, based on the links used in your application code.

This guide will explain how prefetching works and show common implementation patterns:

Automatic prefetch
Manual prefetch
Hover-triggered prefetch
Extending or ejecting link
Disabled prefetch
How does prefetching work?
When navigating between routes, the browser requests assets for the page like HTML and JavaScript files. Prefetching is the process of fetching these resources ahead of time, before you navigate to a new route.

Next.js automatically splits your application into smaller JavaScript chunks based on routes. Instead of loading all the code upfront like traditional SPAs, only the code needed for the current route is loaded. This reduces the initial load time while other parts of the app are loaded in the background. By the time you click the link, the resources for the new route have already been loaded into the browser cache.

When navigating to the new page, there's no full page reload or browser loading spinner. Instead, Next.js performs a client-side transition, making the page navigation feel instant.

Prefetching static vs. dynamic routes
Static page	Dynamic page
Prefetched	Yes, full route	No, unless loading.js
Client Cache TTL	5 min (default)	Off, unless enabled
Server roundtrip on click	No	Yes, streamed after shell
Good to know: During the initial navigation, the browser fetches the HTML, JavaScript, and React Server Components (RSC) Payload. For subsequent navigations, the browser will fetch the RSC Payload for Server Components and JS bundle for Client Components.

Automatic prefetch
app/ui/nav-link.tsx
TypeScript

TypeScript

import Link from 'next/link'
 
export default function NavLink() {
  return <Link href="/about">About</Link>
}
Context	Prefetched payload	Client Cache TTL
No loading.js	Entire page	Until app reload
With loading.js	Layout to first loading boundary	30s (configurable)
Automatic prefetching runs only in production. Disable with prefetch={false} or use the wrapper in Disabled Prefetch.

Manual prefetch

'use client'
 
import { useRouter } from 'next/navigation'
 
const router = useRouter()
router.prefetch('/pricing')
Call router.prefetch() to warm routes outside the viewport or in response to analytics, hover, scroll, etc.

Hover-triggered prefetch
Proceed with caution: Extending Link opts you into maintaining prefetching, cache invalidation, and accessibility concerns. Proceed only if defaults are insufficient.

Next.js tries to do the right prefetching by default, but power users can eject and modify based on their needs. You have the control between performance and resource consumption.

For example, you might have to only trigger prefetches on hover, instead of when entering the viewport (the default behavior):


'use client'
 
import Link from 'next/link'
import { useState } from 'react'
 
export function HoverPrefetchLink({
  href,
  children,
}: {
  href: string
  children: React.ReactNode
}) {
  const [active, setActive] = useState(false)
 
  return (
    <Link
      href={href}
      prefetch={active ? null : false}
      onMouseEnter={() => setActive(true)}
    >
      {children}
    </Link>
  )
}
prefetch={null} restores default (static) prefetching once the user shows intent.

Extending or ejecting link
You can extend the <Link> component to create your own custom prefetching strategy. For example, using the ForesightJS library which prefetches links by predicting the direction of the user's cursor.

Alternatively, you can use useRouter to recreate some of the native <Link> behavior. However, be aware this opts you into maintaining prefetching and cache invalidation.


'use client'
 
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
 
function ManualPrefetchLink({
  href,
  children,
}: {
  href: string
  children: React.ReactNode
}) {
  const router = useRouter()
 
  useEffect(() => {
    let cancelled = false
    const poll = () => {
      if (!cancelled) router.prefetch(href, { onInvalidate: poll })
    }
    poll()
    return () => {
      cancelled = true
    }
  }, [href, router])
 
  return (
    <a
      href={href}
      onClick={(event) => {
        event.preventDefault()
        router.push(href)
      }}
    >
      {children}
    </a>
  )
}
onInvalidate is invoked when Next.js suspects cached data is stale, allowing you to refresh the prefetch.

Good to know: Using an a tag will cause a full page navigation to the destination route, you can use onClick to prevent the full page navigation, and then invoke router.push to navigate to the destination.

Disabled prefetch
You can fully disable prefetching for certain routes for more fine-grained control over resource consumption.


'use client'
 
import Link, { LinkProps } from 'next/link'
 
function NoPrefetchLink({
  prefetch,
  ...rest
}: LinkProps & { children: React.ReactNode }) {
  return <Link {...rest} prefetch={false} />
}
For example, you may still want to have consistent usage of <Link> in your application, but links in your footer might not need to be prefetched when entering the viewport.

Prefetching optimizations
Good to know: Layout deduplication and prefetch scheduling are part of upcoming optimizations. Currently available in Next.js canary via the experimental.clientSegmentCache flag.

Client cache
Next.js stores prefetched React Server Component payloads in memory, keyed by route segments. When navigating between sibling routes (e.g. /dashboard/settings → /dashboard/analytics), it reuses the parent layout and only fetches the updated leaf page. This reduces network traffic and improves navigation speed.

Prefetch scheduling
Next.js maintains a small task queue, which prefetches in the following order:

Links in the viewport
Links showing user intent (hover or touch)
Newer links replace older ones
Links scrolled off-screen are discarded
The scheduler prioritizes likely navigations while minimizing unused downloads.

Partial Prerendering (PPR)
When PPR is enabled, a page is divided into a static shell and a streamed dynamic section:

The shell, which can be prefetched, streams immediately
Dynamic data streams when ready
Data invalidations (revalidateTag, revalidatePath) silently refresh associated prefetches
Troubleshooting
Triggering unwanted side-effects during prefetching
If your layouts or pages are not pure and have side-effects (e.g. tracking analytics), these might be triggered when the route is prefetched, not when the user visits the page.

To avoid this, you should move side-effects to a useEffect hook or a Server Action triggered from a Client Component.

Before:

app/dashboard/layout.tsx
TypeScript

TypeScript

import { trackPageView } from '@/lib/analytics'
 
export default function Layout({ children }: { children: React.ReactNode }) {
  // This runs during prefetch
  trackPageView()
 
  return <div>{children}</div>
}
After:

app/ui/analytics-tracker.tsx
TypeScript

TypeScript

'use client'
 
import { useEffect } from 'react'
import { trackPageView } from '@/lib/analytics'
 
export function AnalyticsTracker() {
  useEffect(() => {
    trackPageView()
  }, [])
 
  return null
}
app/dashboard/layout.tsx
TypeScript

TypeScript

import { AnalyticsTracker } from '@/app/ui/analytics-tracker'
 
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <AnalyticsTracker />
      {children}
    </div>
  )
}
Preventing too many prefetches
Next.js automatically prefetches links in the viewport when using the <Link> component.

There may be cases where you want to prevent this to avoid unnecessary usage of resources, such as when rendering a large list of links (e.g. an infinite scroll table).

You can disable prefetching by setting the prefetch prop of the <Link> component to false.

app/ui/no-prefetch-link.tsx
TypeScript

TypeScript

<Link prefetch={false} href={`/blog/${post.id}`}>
  {post.title}
</Link>
However, this means static routes will only be fetched on click, and dynamic routes will wait for the server to render before navigating.

To reduce resource usage without disabling prefetch entirely, you can defer prefetching until the user hovers over a link. This targets only links the user is likely to visit.

app/ui/hover-prefetch-link.tsx
TypeScript

TypeScript

'use client'
 
import Link from 'next/link'
import { useState } from 'react'
 
export function HoverPrefetchLink({
  href,
  children,
}: {
  href: string
  children: React.ReactNode
}) {
  const [active, setActive] = useState(false)
 
  return (
    <Link
      href={href}
      prefetch={active ? null : false}
      onMouseEnter={() => setActive(true)}
    >
      {children}
    </Link>
  )
}
Previous
Package Bundling
Next
Production
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Guides: Prefetching | Next.js


Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
Analytics
Authentication
Backend for Frontend
Caching
CI Build Caching
Content Security Policy
CSS-in-JS
Custom Server
Data Security
Debugging
Draft Mode
Environment Variables
Forms
ISR
Instrumentation
Internationalization
JSON-LD
Lazy Loading
Development Environment
MDX
Memory Usage
Migrating
App Router
Create React App
Vite
Multi-tenant
Multi-zones
OpenTelemetry
Package Bundling
Prefetching
Production
PWAs
Redirecting
Sass
Scripts
Self-Hosting
SPAs
Static Exports
Tailwind CSS v3
Testing
Cypress
Jest
Playwright
Vitest
Third Party Libraries
Upgrading
Codemods
Version 14
Version 15
Videos
API Reference
Directives
Components
Font
Form Component
Image Component
Link Component
Script Component
File-system conventions
default.js
Dynamic Segments
error.js
forbidden.js
instrumentation.js
instrumentation-client.js
Intercepting Routes
layout.js
loading.js
mdx-components.js
middleware.js
not-found.js
page.js
Parallel Routes
public
route.js
Route Groups
Route Segment Config
src
template.js
unauthorized.js
Metadata Files
Functions
Configuration
next.config.js
TypeScript
ESLint
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
Data fetching approaches
External HTTP APIs
Data Access Layer
Component-level data access
Reading data
Passing data from server to client
Tainting
Preventing client-side execution of server-only code
Mutating Data
Built-in Server Actions Security features
Validating client input
Authentication and authorization
Closures and encryption
Overwriting encryption keys (advanced)
Allowed origins (advanced)
Avoiding side-effects during rendering
Auditing
Next Steps
Edit this page on GitHub
Scroll to top
App Router
Guides
Data Security
How to think about data security in Next.js
React Server Components improve performance and simplify data fetching, but also shift where and how data is accessed, changing some of the traditional security assumptions for handling data in frontend apps.

This guide will help you understand how to think about data security in Next.js and how to implement best practices.

Data fetching approaches
There are three main approaches we recommend for fetching data in Next.js, depending on the size and age of your project:

HTTP APIs: for existing large applications and organizations.
Data Access Layer: for new projects.
Component-Level Data Access: for prototypes and learning.
We recommend choosing one data fetching approach and avoiding mixing them. This makes it clear for both developers working in your code base and security auditors what to expect.

External HTTP APIs
You should follow a Zero Trust model when adopting Server Components in an existing project. You can continue calling your existing API endpoints such as REST or GraphQL from Server Components using fetch, just as you would in Client Components.

app/page.tsx

import { cookies } from 'next/headers'
 
export default async function Page() {
  const cookieStore = cookies()
  const token = cookieStore.get('AUTH_TOKEN')?.value
 
  const res = await fetch('https://api.example.com/profile', {
    headers: {
      Cookie: `AUTH_TOKEN=${token}`,
      // Other headers
    },
  })
 
  // ....
}
This approach works well when:

You already have security practices in place.
Separate backend teams use other languages or manage APIs independently.
Data Access Layer
For new projects, we recommend creating a dedicated Data Access Layer (DAL). This is a internal library that controls how and when data is fetched, and what gets passed to your render context.

A Data Access Layer should:

Only run on the server.
Perform authorization checks.
Return safe, minimal Data Transfer Objects (DTOs).
This approach centralizes all data access logic, making it easier to enforce consistent data access and reduces the risk of authorization bugs. You also get the benefit of sharing an in-memory cache across different parts of a request.

data/auth.ts

import { cache } from 'react'
import { cookies } from 'next/headers'
 
// Cached helper methods makes it easy to get the same value in many places
// without manually passing it around. This discourages passing it from Server
// Component to Server Component which minimizes risk of passing it to a Client
// Component.
export const getCurrentUser = cache(async () => {
  const token = cookies().get('AUTH_TOKEN')
  const decodedToken = await decryptAndValidate(token)
  // Don't include secret tokens or private information as public fields.
  // Use classes to avoid accidentally passing the whole object to the client.
  return new User(decodedToken.id)
})
data/user-dto.tsx

import 'server-only'
import { getCurrentUser } from './auth'
 
function canSeeUsername(viewer: User) {
  // Public info for now, but can change
  return true
}
 
function canSeePhoneNumber(viewer: User, team: string) {
  // Privacy rules
  return viewer.isAdmin || team === viewer.team
}
 
export async function getProfileDTO(slug: string) {
  // Don't pass values, read back cached values, also solves context and easier to make it lazy
 
  // use a database API that supports safe templating of queries
  const [rows] = await sql`SELECT * FROM user WHERE slug = ${slug}`
  const userData = rows[0]
 
  const currentUser = await getCurrentUser()
 
  // only return the data relevant for this query and not everything
  // <https://www.w3.org/2001/tag/doc/APIMinimization>
  return {
    username: canSeeUsername(currentUser) ? userData.username : null,
    phonenumber: canSeePhoneNumber(currentUser, userData.team)
      ? userData.phonenumber
      : null,
  }
}
app/page.tsx

import { getProfile } from '../../data/user'
 
export async function Page({ params: { slug } }) {
  // This page can now safely pass around this profile knowing
  // that it shouldn't contain anything sensitive.
  const profile = await getProfile(slug);
  ...
}
Good to know: Secret keys should be stored in environment variables, but only the Data Access Layer should access process.env. This keeps secrets from being exposed to other parts of the application.

Component-level data access
For quick prototypes and iteration, database queries can be placed directly in Server Components.

This approach, however, makes it easier to accidentally expose private data to the client, for example:

app/page.tsx

import Profile from './components/profile.tsx'
 
export async function Page({ params: { slug } }) {
  const [rows] = await sql`SELECT * FROM user WHERE slug = ${slug}`
  const userData = rows[0]
  // EXPOSED: This exposes all the fields in userData to the client because
  // we are passing the data from the Server Component to the Client.
  return <Profile user={userData} />
}
app/ui/profile.tsx

'use client'
 
// BAD: This is a bad props interface because it accepts way more data than the
// Client Component needs and it encourages server components to pass all that
// data down. A better solution would be to accept a limited object with just
// the fields necessary for rendering the profile.
export default async function Profile({ user }: { user: User }) {
  return (
    <div>
      <h1>{user.name}</h1>
      ...
    </div>
  )
}
You should sanitize the data before passing it to the Client Component:

data/user.ts

import { sql } from './db'
 
export async function getUser(slug: string) {
  const [rows] = await sql`SELECT * FROM user WHERE slug = ${slug}`
  const user = rows[0]
 
  // Return only the public fields
  return {
    name: user.name,
  }
}
app/page.tsx

import { getUser } from '../data/user'
import Profile from './ui/profile'
 
export default async function Page({
  params: { slug },
}: {
  params: { slug: string }
}) {
  const publicProfile = await getUser(slug)
  return <Profile user={publicProfile} />
}
Reading data
Passing data from server to client
On the initial load, both Server and Client Components run on the server to generate HTML. However, they execute in isolated module systems. This ensures that Server Components can access private data and APIs, while Client Components cannot.

Server Components:

Run only on the server.
Can safely access environment variables, secrets, databases, and internal APIs.
Client Components:

Run on the server during pre-rendering, but must follow the same security assumptions as code running in the browser.
Must not access privileged data or server-only modules.
This ensures the app is secure by default, but it's possible to accidentally expose private data through how data is fetched or passed to components.

Tainting
To prevent accidental exposure of private data to the client, you can use React Taint APIs:

experimental_taintObjectReference for data objects.
experimental_taintUniqueValue for specific values.
You can enable usage in your Next.js app with the experimental.taint option in next.config.js:

next.config.js

module.exports = {
  experimental: {
    taint: true,
  },
}
This prevents the tainted objects or values from being passed to the client. However, it's an additional layer of protection, you should still filter and sanitize the data in your DAL before passing it to React's render context.

Good to know:

By default, environment variables are only available on the Server. Next.js exposes any environment variable prefixed with NEXT_PUBLIC_ to the client. Learn more.
Functions and classes are already blocked from being passed to Client Components by default.
Preventing client-side execution of server-only code
To prevent server-only code from being executed on the client, you can mark a module with the server-only package:

pnpm
npm
yarn
bun
Terminal

pnpm add server-only
lib/data.ts

import 'server-only'
 
//...
This ensures that proprietary code or internal business logic stays on the server by causing a build error if the module is imported in the client environment.

Mutating Data
Next.js handles mutations with Server Actions.

Built-in Server Actions Security features
By default, when a Server Action is created and exported, it creates a public HTTP endpoint and should be treated with the same security assumptions and authorization checks. This means, even if a Server Action or utility function is not imported elsewhere in your code, it's still publicly accessible.

To improve security, Next.js has the following built-in features:

Secure action IDs: Next.js creates encrypted, non-deterministic IDs to allow the client to reference and call the Server Action. These IDs are periodically recalculated between builds for enhanced security.
Dead code elimination: Unused Server Actions (referenced by their IDs) are removed from client bundle to avoid public access.
Good to know:

The IDs are created during compilation and are cached for a maximum of 14 days. They will be regenerated when a new build is initiated or when the build cache is invalidated. This security improvement reduces the risk in cases where an authentication layer is missing. However, you should still treat Server Actions like public HTTP endpoints.


// app/actions.js
'use server'
 
// If this action **is** used in our application, Next.js
// will create a secure ID to allow the client to reference
// and call the Server Action.
export async function updateUserAction(formData) {}
 
// If this action **is not** used in our application, Next.js
// will automatically remove this code during `next build`
// and will not create a public endpoint.
export async function deleteUserAction(formData) {}
Validating client input
You should always validate input from client, as they can be easily modified. For example, form data, URL parameters, headers, and searchParams:

app/page.tsx

// BAD: Trusting searchParams directly
export default async function Page({ searchParams }) {
  const isAdmin = searchParams.get('isAdmin')
  if (isAdmin === 'true') {
    // Vulnerable: relies on untrusted client data
    return <AdminPanel />
  }
}
 
// GOOD: Re-verify every time
import { cookies } from 'next/headers'
import { verifyAdmin } from './auth'
 
export default async function Page() {
  const token = cookies().get('AUTH_TOKEN')
  const isAdmin = await verifyAdmin(token)
 
  if (isAdmin) {
    return <AdminPanel />
  }
}
Authentication and authorization
You should always ensure that a user is authorized to perform an action. For example:

app/actions.ts

'use server'
 
import { auth } from './lib'
 
export function addItem() {
  const { user } = auth()
  if (!user) {
    throw new Error('You must be signed in to perform this action')
  }
 
  // ...
}
Learn more about Authentication in Next.js.

Closures and encryption
Defining a Server Action inside a component creates a closure where the action has access to the outer function's scope. For example, the publish action has access to the publishVersion variable:

app/page.tsx
TypeScript

TypeScript

export default async function Page() {
  const publishVersion = await getLatestVersion();
 
  async function publish() {
    "use server";
    if (publishVersion !== await getLatestVersion()) {
      throw new Error('The version has changed since pressing publish');
    }
    ...
  }
 
  return (
    <form>
      <button formAction={publish}>Publish</button>
    </form>
  );
}
Closures are useful when you need to capture a snapshot of data (e.g. publishVersion) at the time of rendering so that it can be used later when the action is invoked.

However, for this to happen, the captured variables are sent to the client and back to the server when the action is invoked. To prevent sensitive data from being exposed to the client, Next.js automatically encrypts the closed-over variables. A new private key is generated for each action every time a Next.js application is built. This means actions can only be invoked for a specific build.

Good to know: We don't recommend relying on encryption alone to prevent sensitive values from being exposed on the client.

Overwriting encryption keys (advanced)
When self-hosting your Next.js application across multiple servers, each server instance may end up with a different encryption key, leading to potential inconsistencies.

To mitigate this, you can overwrite the encryption key using the process.env.NEXT_SERVER_ACTIONS_ENCRYPTION_KEY environment variable. Specifying this variable ensures that your encryption keys are persistent across builds, and all server instances use the same key. This variable must be AES-GCM encrypted.

This is an advanced use case where consistent encryption behavior across multiple deployments is critical for your application. You should consider standard security practices such key rotation and signing.

Good to know: Next.js applications deployed to Vercel automatically handle this.

Allowed origins (advanced)
Since Server Actions can be invoked in a <form> element, this opens them up to CSRF attacks.

Behind the scenes, Server Actions use the POST method, and only this HTTP method is allowed to invoke them. This prevents most CSRF vulnerabilities in modern browsers, particularly with SameSite cookies being the default.

As an additional protection, Server Actions in Next.js also compare the Origin header to the Host header (or X-Forwarded-Host). If these don't match, the request will be aborted. In other words, Server Actions can only be invoked on the same host as the page that hosts it.

For large applications that use reverse proxies or multi-layered backend architectures (where the server API differs from the production domain), it's recommended to use the configuration option serverActions.allowedOrigins option to specify a list of safe origins. The option accepts an array of strings.

next.config.js

/** @type {import('next').NextConfig} */
module.exports = {
  experimental: {
    serverActions: {
      allowedOrigins: ['my-proxy.com', '*.my-proxy.com'],
    },
  },
}
Learn more about Security and Server Actions.

Avoiding side-effects during rendering
Mutations (e.g. logging out users, updating databases, invalidating caches) should never be a side-effect, either in Server or Client Components. Next.js explicitly prevents setting cookies or triggering cache revalidation within render methods to avoid unintended side effects.

app/page.tsx

// BAD: Triggering a mutation during rendering
export default async function Page({ searchParams }) {
  if (searchParams.get('logout')) {
    cookies().delete('AUTH_TOKEN')
  }
 
  return <UserProfile />
}
Instead, you should use Server Actions to handle mutations.

app/page.tsx

// GOOD: Using Server Actions to handle mutations
import { logout } from './actions'
 
export default function Page() {
  return (
    <>
      <UserProfile />
      <form action={logout}>
        <button type="submit">Logout</button>
      </form>
    </>
  )
}
Good to know: Next.js uses POST requests to handle mutations. This prevents accidental side-effects from GET requests, reducing Cross-Site Request Forgery (CSRF) risks.

Auditing
If you're doing an audit of a Next.js project, here are a few things we recommend looking extra at:

Data Access Layer: Is there an established practice for an isolated Data Access Layer? Verify that database packages and environment variables are not imported outside the Data Access Layer.
"use client" files: Are the Component props expecting private data? Are the type signatures overly broad?
"use server" files: Are the Action arguments validated in the action or inside the Data Access Layer? Is the user re-authorized inside the action?
/[param]/. Folders with brackets are user input. Are params validated?
middleware.ts and route.ts: Have a lot of power. Spend extra time auditing these using traditional techniques. Perform Penetration Testing or Vulnerability Scanning regularly or in alignment with your team's software development lifecycle.
Next Steps
Learn more about the topics mentioned in this guide.
Authentication
Learn how to implement authentication in your Next.js application.
Content Security Policy
Learn how to set a Content Security Policy (CSP) for your Next.js application.
Forms
Learn how to create forms in Next.js with React Server Actions.
Previous
Custom Server
Next
Debugging
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Guides: Data Security | Next.js

Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K

Using App Router

Features available in /app


Latest Version

15.5.4

Getting Started
Installation
Project Structure
Layouts and Pages
Linking and Navigating
Server and Client Components
Partial Prerendering
Fetching Data
Updating Data
Caching and Revalidating
Error Handling
CSS
Image Optimization
Font Optimization
Metadata and OG images
Route Handlers and Middleware
Deploying
Upgrading
Guides
Analytics
Authentication
Backend for Frontend
Caching
CI Build Caching
Content Security Policy
CSS-in-JS
Custom Server
Data Security
Debugging
Draft Mode
Environment Variables
Forms
ISR
Instrumentation
Internationalization
JSON-LD
Lazy Loading
Development Environment
MDX
Memory Usage
Migrating
App Router
Create React App
Vite
Multi-tenant
Multi-zones
OpenTelemetry
Package Bundling
Prefetching
Production
PWAs
Redirecting
Sass
Scripts
Self-Hosting
SPAs
Static Exports
Tailwind CSS v3
Testing
Cypress
Jest
Playwright
Vitest
Third Party Libraries
Upgrading
Codemods
Version 14
Version 15
Videos
API Reference
Directives
Components
Font
Form Component
Image Component
Link Component
Script Component
File-system conventions
default.js
Dynamic Segments
error.js
forbidden.js
instrumentation.js
instrumentation-client.js
Intercepting Routes
layout.js
loading.js
mdx-components.js
middleware.js
not-found.js
page.js
Parallel Routes
public
route.js
Route Groups
Route Segment Config
src
template.js
unauthorized.js
Metadata Files
Functions
Configuration
next.config.js
TypeScript
ESLint
CLI
Edge Runtime
Turbopack
Architecture
Accessibility
Fast Refresh
Next.js Compiler
Supported Browsers
Community
Contribution Guide
Rspack
On this page
Configuration
Supported Features
Server Components
Client Components
Image Optimization
Route Handlers
Browser APIs
Unsupported Features
Deploying
Version History
Edit this page on GitHub
Scroll to top
App Router
Guides
Static Exports
How to create a static export of your Next.js application
Next.js enables starting as a static site or Single-Page Application (SPA), then later optionally upgrading to use features that require a server.

When running next build, Next.js generates an HTML file per route. By breaking a strict SPA into individual HTML files, Next.js can avoid loading unnecessary JavaScript code on the client-side, reducing the bundle size and enabling faster page loads.

Since Next.js supports this static export, it can be deployed and hosted on any web server that can serve HTML/CSS/JS static assets.

Configuration
To enable a static export, change the output mode inside next.config.js:

next.config.js

/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  output: 'export',
 
  // Optional: Change links `/me` -> `/me/` and emit `/me.html` -> `/me/index.html`
  // trailingSlash: true,
 
  // Optional: Prevent automatic `/me` -> `/me/`, instead preserve `href`
  // skipTrailingSlashRedirect: true,
 
  // Optional: Change the output directory `out` -> `dist`
  // distDir: 'dist',
}
 
module.exports = nextConfig
After running next build, Next.js will create an out folder with the HTML/CSS/JS assets for your application.

Supported Features
The core of Next.js has been designed to support static exports.

Server Components
When you run next build to generate a static export, Server Components consumed inside the app directory will run during the build, similar to traditional static-site generation.

The resulting component will be rendered into static HTML for the initial page load and a static payload for client navigation between routes. No changes are required for your Server Components when using the static export, unless they consume dynamic server functions.

app/page.tsx
TypeScript

TypeScript

export default async function Page() {
  // This fetch will run on the server during `next build`
  const res = await fetch('https://api.example.com/...')
  const data = await res.json()
 
  return <main>...</main>
}
Client Components
If you want to perform data fetching on the client, you can use a Client Component with SWR to memoize requests.

app/other/page.tsx
TypeScript

TypeScript

'use client'
 
import useSWR from 'swr'
 
const fetcher = (url: string) => fetch(url).then((r) => r.json())
 
export default function Page() {
  const { data, error } = useSWR(
    `https://jsonplaceholder.typicode.com/posts/1`,
    fetcher
  )
  if (error) return 'Failed to load'
  if (!data) return 'Loading...'
 
  return data.title
}
Since route transitions happen client-side, this behaves like a traditional SPA. For example, the following index route allows you to navigate to different posts on the client:

app/page.tsx
TypeScript

TypeScript

import Link from 'next/link'
 
export default function Page() {
  return (
    <>
      <h1>Index Page</h1>
      <hr />
      <ul>
        <li>
          <Link href="/post/1">Post 1</Link>
        </li>
        <li>
          <Link href="/post/2">Post 2</Link>
        </li>
      </ul>
    </>
  )
}
Image Optimization
Image Optimization through next/image can be used with a static export by defining a custom image loader in next.config.js. For example, you can optimize images with a service like Cloudinary:

next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    loader: 'custom',
    loaderFile: './my-loader.ts',
  },
}
 
module.exports = nextConfig
This custom loader will define how to fetch images from a remote source. For example, the following loader will construct the URL for Cloudinary:

my-loader.ts
TypeScript

TypeScript

export default function cloudinaryLoader({
  src,
  width,
  quality,
}: {
  src: string
  width: number
  quality?: number
}) {
  const params = ['f_auto', 'c_limit', `w_${width}`, `q_${quality || 'auto'}`]
  return `https://res.cloudinary.com/demo/image/upload/${params.join(
    ','
  )}${src}`
}
You can then use next/image in your application, defining relative paths to the image in Cloudinary:

app/page.tsx
TypeScript

TypeScript

import Image from 'next/image'
 
export default function Page() {
  return <Image alt="turtles" src="/turtles.jpg" width={300} height={300} />
}
Route Handlers
Route Handlers will render a static response when running next build. Only the GET HTTP verb is supported. This can be used to generate static HTML, JSON, TXT, or other files from cached or uncached data. For example:

app/data.json/route.ts
TypeScript

TypeScript

export async function GET() {
  return Response.json({ name: 'Lee' })
}
The above file app/data.json/route.ts will render to a static file during next build, producing data.json containing { name: 'Lee' }.

If you need to read dynamic values from the incoming request, you cannot use a static export.

Browser APIs
Client Components are pre-rendered to HTML during next build. Because Web APIs like window, localStorage, and navigator are not available on the server, you need to safely access these APIs only when running in the browser. For example:


'use client';
 
import { useEffect } from 'react';
 
export default function ClientComponent() {
  useEffect(() => {
    // You now have access to `window`
    console.log(window.innerHeight);
  }, [])
 
  return ...;
}
Unsupported Features
Features that require a Node.js server, or dynamic logic that cannot be computed during the build process, are not supported:

Dynamic Routes with dynamicParams: true
Dynamic Routes without generateStaticParams()
Route Handlers that rely on Request
Cookies
Rewrites
Redirects
Headers
Middleware
Incremental Static Regeneration
Image Optimization with the default loader
Draft Mode
Server Actions
Intercepting Routes
Attempting to use any of these features with next dev will result in an error, similar to setting the dynamic option to error in the root layout.


export const dynamic = 'error'
Deploying
With a static export, Next.js can be deployed and hosted on any web server that can serve HTML/CSS/JS static assets.

When running next build, Next.js generates the static export into the out folder. For example, let's say you have the following routes:

/
/blog/[id]
After running next build, Next.js will generate the following files:

/out/index.html
/out/404.html
/out/blog/post-1.html
/out/blog/post-2.html
If you are using a static host like Nginx, you can configure rewrites from incoming requests to the correct files:

nginx.conf

server {
  listen 80;
  server_name acme.com;
 
  root /var/www/out;
 
  location / {
      try_files $uri $uri.html $uri/ =404;
  }
 
  # This is necessary when `trailingSlash: false`.
  # You can omit this when `trailingSlash: true`.
  location /blog/ {
      rewrite ^/blog/(.*)$ /blog/$1.html break;
  }
 
  error_page 404 /404.html;
  location = /404.html {
      internal;
  }
}
Version History
Version	Changes
v14.0.0	next export has been removed in favor of "output": "export"
v13.4.0	App Router (Stable) adds enhanced static export support, including using React Server Components and Route Handlers.
v13.3.0	next export is deprecated and replaced with "output": "export"
Previous
SPAs
Next
Tailwind CSS v3
Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




Guides: Static Exports | Next.js


Skip to content
Showcase
Docs
Blog
Templates
Enterprise
Search documentation...
⌘K
Chapter 9

Streaming

9

Chapter 9

Streaming
In the previous chapter, you learned about the different rendering methods of Next.js. We also discussed how slow data fetches can impact the performance of your application. Let's look at how you can improve the user experience when there are slow data requests.

In this chapter...

Here are the topics we’ll cover

What streaming is and when you might use it.

How to implement streaming with loading.tsx and Suspense.

What loading skeletons are.

What Next.js Route Groups are, and when you might use them.

Where to place React Suspense boundaries in your application.

What is streaming?
Streaming is a data transfer technique that allows you to break down a route into smaller "chunks" and progressively stream them from the server to the client as they become ready.

Diagram showing time with sequential data fetching and parallel data fetching
By streaming, you can prevent slow data requests from blocking your whole page. This allows the user to see and interact with parts of the page without waiting for all the data to load before any UI can be shown to the user.

Diagram showing time with sequential data fetching and parallel data fetching
Streaming works well with React's component model, as each component can be considered a chunk.

There are two ways you implement streaming in Next.js:

At the page level, with the loading.tsx file (which creates <Suspense> for you).
At the component level, with <Suspense> for more granular control.
Let's see how this works.

It’s time to take a quiz!
Test your knowledge and see what you’ve just learned.

What is one advantage of streaming?


A
Data requests become more secure through chunk encryption

B
All chunks are rendered only after they are received in full

C
Chunks are rendered in parallel, reducing the overall load time
Streaming a whole page with loading.tsx
In the /app/dashboard folder, create a new file called loading.tsx:

/app/dashboard/loading.tsx

export default function Loading() {
  return <div>Loading...</div>;
}
Refresh http://localhost:3000/dashboard, and you should now see:

Dashboard page with 'Loading...' text
A few things are happening here:

loading.tsx is a special Next.js file built on top of React Suspense. It allows you to create fallback UI to show as a replacement while page content loads.
Since <SideNav> is static, it's shown immediately. The user can interact with <SideNav> while the dynamic content is loading.
The user doesn't have to wait for the page to finish loading before navigating away (this is called interruptable navigation).
Congratulations! You've just implemented streaming. But we can do more to improve the user experience. Let's show a loading skeleton instead of the Loading… text.

Adding loading skeletons
A loading skeleton is a simplified version of the UI. Many websites use them as a placeholder (or fallback) to indicate to users that the content is loading. Any UI you add in loading.tsx will be embedded as part of the static file, and sent first. Then, the rest of the dynamic content will be streamed from the server to the client.

Inside your loading.tsx file, import a new component called <DashboardSkeleton>:

/app/dashboard/loading.tsx

import DashboardSkeleton from '@/app/ui/skeletons';
 
export default function Loading() {
  return <DashboardSkeleton />;
}
Then, refresh http://localhost:3000/dashboard, and you should now see:

Dashboard page with loading skeletons
Fixing the loading skeleton bug with route groups
Right now, your loading skeleton will apply to the invoices.

Since loading.tsx is a level higher than /invoices/page.tsx and /customers/page.tsx in the file system, it's also applied to those pages.

We can change this with Route Groups. Create a new folder called /(overview) inside the dashboard folder. Then, move your loading.tsx and page.tsx files inside the folder:

Folder structure showing how to create a route group using parentheses
Now, the loading.tsx file will only apply to your dashboard overview page.

Route groups allow you to organize files into logical groups without affecting the URL path structure. When you create a new folder using parentheses (), the name won't be included in the URL path. So /dashboard/(overview)/page.tsx becomes /dashboard.

Here, you're using a route group to ensure loading.tsx only applies to your dashboard overview page. However, you can also use route groups to separate your application into sections (e.g. (marketing) routes and (shop) routes) or by teams for larger applications.

Streaming a component
So far, you're streaming a whole page. But you can also be more granular and stream specific components using React Suspense.

Suspense allows you to defer rendering parts of your application until some condition is met (e.g. data is loaded). You can wrap your dynamic components in Suspense. Then, pass it a fallback component to show while the dynamic component loads.

If you remember the slow data request, fetchRevenue(), this is the request that is slowing down the whole page. Instead of blocking your whole page, you can use Suspense to stream only this component and immediately show the rest of the page's UI.

To do so, you'll need to move the data fetch to the component, let's update the code to see what that'll look like:

Delete all instances of fetchRevenue() and its data from /dashboard/(overview)/page.tsx:

/app/dashboard/(overview)/page.tsx

import { Card } from '@/app/ui/dashboard/cards';
import RevenueChart from '@/app/ui/dashboard/revenue-chart';
import LatestInvoices from '@/app/ui/dashboard/latest-invoices';
import { lusitana } from '@/app/ui/fonts';
import { fetchLatestInvoices, fetchCardData } from '@/app/lib/data'; // remove fetchRevenue
 
export default async function Page() {
  const revenue = await fetchRevenue() // delete this line
  const latestInvoices = await fetchLatestInvoices();
  const {
    numberOfInvoices,
    numberOfCustomers,
    totalPaidInvoices,
    totalPendingInvoices,
  } = await fetchCardData();
 
  return (
    // ...
  );
}
Then, import <Suspense> from React, and wrap it around <RevenueChart />. You can pass it a fallback component called <RevenueChartSkeleton>.

/app/dashboard/(overview)/page.tsx

import { Card } from '@/app/ui/dashboard/cards';
import RevenueChart from '@/app/ui/dashboard/revenue-chart';
import LatestInvoices from '@/app/ui/dashboard/latest-invoices';
import { lusitana } from '@/app/ui/fonts';
import { fetchLatestInvoices, fetchCardData } from '@/app/lib/data';
import { Suspense } from 'react';
import { RevenueChartSkeleton } from '@/app/ui/skeletons';
 
export default async function Page() {
  const latestInvoices = await fetchLatestInvoices();
  const {
    numberOfInvoices,
    numberOfCustomers,
    totalPaidInvoices,
    totalPendingInvoices,
  } = await fetchCardData();
 
  return (
    <main>
      <h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
        Dashboard
      </h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Collected" value={totalPaidInvoices} type="collected" />
        <Card title="Pending" value={totalPendingInvoices} type="pending" />
        <Card title="Total Invoices" value={numberOfInvoices} type="invoices" />
        <Card
          title="Total Customers"
          value={numberOfCustomers}
          type="customers"
        />
      </div>
      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-4 lg:grid-cols-8">
        <Suspense fallback={<RevenueChartSkeleton />}>
          <RevenueChart />
        </Suspense>
        <LatestInvoices latestInvoices={latestInvoices} />
      </div>
    </main>
  );
}
Finally, update the <RevenueChart> component to fetch its own data and remove the prop passed to it:

/app/ui/dashboard/revenue-chart.tsx

import { generateYAxis } from '@/app/lib/utils';
import { CalendarIcon } from '@heroicons/react/24/outline';
import { lusitana } from '@/app/ui/fonts';
import { fetchRevenue } from '@/app/lib/data';
 
// ...
 
export default async function RevenueChart() { // Make component async, remove the props
  const revenue = await fetchRevenue(); // Fetch data inside the component
 
  const chartHeight = 350;
  const { yAxisLabels, topLabel } = generateYAxis(revenue);
 
  if (!revenue || revenue.length === 0) {
    return <p className="mt-4 text-gray-400">No data available.</p>;
  }
 
  return (
    // ...
  );
}
 
Now refresh the page, you should see the dashboard information almost immediately, while a fallback skeleton is shown for <RevenueChart>:

Dashboard page with revenue chart skeleton and loaded Card and Latest Invoices components
Practice: Streaming <LatestInvoices>
Now it's your turn! Practice what you've just learned by streaming the <LatestInvoices> component.

Move fetchLatestInvoices() down from the page to the <LatestInvoices> component. Wrap the component in a <Suspense> boundary with a fallback called <LatestInvoicesSkeleton>.

Once you're ready, expand the toggle to see the solution code:

Grouping components
Great! You're almost there, now you need to wrap the <Card> components in Suspense. You can fetch data for each individual card, but this could lead to a popping effect as the cards load in, this can be visually jarring for the user.

So, how would you tackle this problem?

To create more of a staggered effect, you can group the cards using a wrapper component. This means the static <SideNav/> will be shown first, followed by the cards, etc.

In your page.tsx file:

Delete your <Card> components.
Delete the fetchCardData() function.
Import a new wrapper component called <CardWrapper />.
Import a new skeleton component called <CardsSkeleton />.
Wrap <CardWrapper /> in Suspense.
/app/dashboard/(overview)/page.tsx

import CardWrapper from '@/app/ui/dashboard/cards';
// ...
import {
  RevenueChartSkeleton,
  LatestInvoicesSkeleton,
  CardsSkeleton,
} from '@/app/ui/skeletons';
 
export default async function Page() {
  return (
    <main>
      <h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
        Dashboard
      </h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Suspense fallback={<CardsSkeleton />}>
          <CardWrapper />
        </Suspense>
      </div>
      // ...
    </main>
  );
}
Then, move into the file /app/ui/dashboard/cards.tsx, import the fetchCardData() function, and invoke it inside the <CardWrapper/> component. Make sure to uncomment any necessary code in this component.

/app/ui/dashboard/cards.tsx

// ...
import { fetchCardData } from '@/app/lib/data';
 
// ...
 
export default async function CardWrapper() {
  const {
    numberOfInvoices,
    numberOfCustomers,
    totalPaidInvoices,
    totalPendingInvoices,
  } = await fetchCardData();
 
  return (
    <>
      <Card title="Collected" value={totalPaidInvoices} type="collected" />
      <Card title="Pending" value={totalPendingInvoices} type="pending" />
      <Card title="Total Invoices" value={numberOfInvoices} type="invoices" />
      <Card
        title="Total Customers"
        value={numberOfCustomers}
        type="customers"
      />
    </>
  );
}
Refresh the page, and you should see all the cards load in at the same time. You can use this pattern when you want multiple components to load in at the same time.

Deciding where to place your Suspense boundaries
Where you place your Suspense boundaries will depend on a few things:

How you want the user to experience the page as it streams.
What content you want to prioritize.
If the components rely on data fetching.
Take a look at your dashboard page, is there anything you would've done differently?

Don't worry. There isn't a right answer.

You could stream the whole page like we did with loading.tsx... but that may lead to a longer loading time if one of the components has a slow data fetch.
You could stream every component individually... but that may lead to UI popping into the screen as it becomes ready.
You could also create a staggered effect by streaming page sections. But you'll need to create wrapper components.
Where you place your suspense boundaries will vary depending on your application. In general, it's good practice to move your data fetches down to the components that need it, and then wrap those components in Suspense. But there is nothing wrong with streaming the sections or the whole page if that's what your application needs.

Don't be afraid to experiment with Suspense and see what works best, it's a powerful API that can help you create more delightful user experiences.

It’s time to take a quiz!
Test your knowledge and see what you’ve just learned.

In general, what is considered good practice when working with Suspense and data fetching?


A
Move data fetches up to the parent component

B
Avoid using Suspense for data fetching

C
Move data fetches down to the components that need it

D
Use Suspense only for error boundaries
Looking ahead
Streaming and Server Components give us new ways to handle data fetching and loading states, ultimately with the goal of improving the end user experience.

In the next chapter, you'll learn about Partial Prerendering, a new Next.js rendering model built with streaming in mind.

9
You've Completed Chapter 9
You've learned how to stream components with Suspense and loading skeletons.

Next Up

10: Partial Prerendering

An early look into Partial Prerendering - a new experimental rendering model built with streaming.

Was this helpful?





Your feedback...
supported.
Resources
Docs
Support Policy
Learn
Showcase
Blog
Team
Analytics
Next.js Conf
Previews
More
Next.js Commerce
Contact Sales
Community
GitHub
Releases
Telemetry
Governance
About Vercel
Next.js + Vercel
Open Source Software
GitHub
Bluesky
X
Legal
Privacy Policy
Cookie Preferences
Subscribe to our newsletter
Stay updated on new releases and features, guides, and case studies.

you@domain.com
Subscribe
© 2025 Vercel, Inc.




[![npm](https://img.shields.io/npm/v/@googlemaps/js-api-loader)][npm-pkg]
[![License](https://img.shields.io/github/license/googlemaps/js-api-loader?color=blue)][license]
![Stable](https://img.shields.io/badge/stability-stable-green)
[![Tests/Build](https://github.com/googlemaps/js-api-loader/actions/workflows/test.yml/badge.svg)](https://github.com/googlemaps/js-api-loader/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/googlemaps/js-api-loader/branch/main/graph/badge.svg)](https://app.codecov.io/gh/googlemaps/js-api-loader/tree/main)
[![StackOverflow](https://img.shields.io/stackexchange/stackoverflow/t/google-maps?color=orange&label=google-maps&logo=stackoverflow)](https://stackoverflow.com/questions/tagged/google-maps)
[![Discord](https://img.shields.io/discord/676948200904589322?color=6A7EC2&logo=discord&logoColor=ffffff)][Discord server]

# Google Maps JavaScript API Loader

## Description

Load the Google Maps JavaScript API script dynamically. This is an npm version
of the [Dynamic Library Import](https://developers.google.com/maps/documentation/javascript/load-maps-js-api#dynamic-library-import)
script.

## Requirements

- [Sign up with Google Maps Platform]
- A Google Cloud Platform [project] with the [**Maps JavaScript API**][maps-sdk]
  enabled
- An [API key] associated with the project above

## Installation

Install [`@googlemaps/js-api-loader`][npm-pkg] with:

```sh
npm install --save @googlemaps/js-api-loader

# or
yarn add @googlemaps/js-api-loader

# or
pnpm add @googlemaps/js-api-loader
```

TypeScript users should additionally install the types for the Google Maps
JavaScript API:

```sh
npm install --save-dev @types/google.maps
```

## Usage

```javascript
import { setOptions, importLibrary } from "@googlemaps/js-api-loader";

// Set the options for loading the API.
setOptions({ key: "your-api-key-here" });

// Load the needed APIs.
// Note: once the returned promise is fulfilled, the libraries are also
//       available in the global `google.maps` namespace.
const { Map } = await importLibrary("maps");
const map = new Map(mapEl, mapOptions);

// Alternatively:
await importLibrary("maps");
const map = new google.maps.Map(mapEl, mapOptions);

// Or, if you prefer using callbacks instead of async/await:
importLibrary("maps").then(({ Map }) => {
  const map = new Map(mapEl, mapOptions);
});
```

If you use custom HTML elements from the Google Maps JavaScript API (e.g.
`<gmp-map>`, and `<gmp-advanced-marker>`), you need to import them as well.
Note that you do not need to await the result of `importLibrary()` in this case.
The custom elements will upgrade automatically once the library is loaded
and you can use the `whenDefined()` method to wait for the upgrade to
complete.

```javascript
import { setOptions, importLibrary } from "@googlemaps/js-api-loader";

// Set the options for loading the API.
setOptions({ key: "your-api-key-here" });

// Start loading the libraries needed for custom elements.
importLibrary("maps"); // needed for <gmp-map>
importLibrary("marker"); // needed for <gmp-advanced-marker>

// Wait for gmp-map to be upgraded and interact with it.
await customElements.whenDefined("gmp-map");
const map = document.querySelector("gmp-map");
// ...
```

## Documentation

This package exports just two functions, `setOptions()` and `importLibrary()`.

```ts
// Using named exports:
import { setOptions, importLibrary } from "@googlemaps/js-api-loader";

setOptions({ key: GOOGLE_MAPS_API_KEY });
await importLibrary("core");
```

### `setOptions(options: APIOptions): void`

Sets the options for loading the Google Maps JavaScript API and installs the
global `google.maps.importLibrary()` function that is used by the
`importLibrary()` function of this package.

This function should be called as early as possible in your application and
should only be called once. Any further calls will not have any effect and
log a warning to the console.

Below is a short summary of the accepted options, see the
[documentation][parameters] for full descriptions and additional information:

- `key: string`: Your API key. This is the only required option.
- `v: string`: The version of the Maps JavaScript API to load.
- `language: string`: The language to use.
- `region: string`: The region code to use.
- `libraries: string[]`: Additional libraries to preload.
- `authReferrerPolicy: string`: Set the referrer policy for the API requests.
- `mapIds: string[]`: An array of map IDs to preload.
- `channel: string`: Can be used to track your usage.
- `solutionChannel: string`: Used by the Google Maps Platform to track
  adoption and usage of examples and solutions.

### `importLibrary(library: string): Promise`

Loads the specified library. Returns a promise that resolves with the
library object when the library is loaded. In case of an error while loading
the library (might be due to poor network conditions and other unforseeable
circumstances), the promise is rejected with an error.

Calling this function for the first time will trigger loading the Google
Maps JavaScript API itself.

The following libraries are available:

- `core`: [`google.maps.CoreLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#CoreLibrary)
- `maps`: [`google.maps.MapsLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#MapsLibrary)
- `maps3d`: [`google.maps.Maps3DLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#Maps3DLibrary)
- `places`: [`google.maps.PlacesLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#PlacesLibrary)
- `geocoding`: [`google.maps.GeocodingLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#GeocodingLibrary)
- `routes`: [`google.maps.RoutesLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#RoutesLibrary)
- `marker`: [`google.maps.MarkerLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#MarkerLibrary)
- `geometry`: [`google.maps.GeometryLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#GeometryLibrary)
- `elevation`: [`google.maps.ElevationLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#ElevationLibrary)
- `streetView`: [`google.maps.StreetViewLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#StreetViewLibrary)
- `journeySharing`: [`google.maps.JourneySharingLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#JourneySharingLibrary)
- `visualization`: [`google.maps.VisualizationLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#VisualizationLibrary)
- `airQuality`: [`google.maps.AirQualityLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#AirQualityLibrary)
- `addressValidation`: [`google.maps.AddressValidationLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#AddressValidationLibrary)
- `drawing`: [`google.maps.DrawingLibrary`](https://developers.google.com/maps/documentation/javascript/reference/library-interfaces#DrawingLibrary) (deprecated)

## Migrating from v1 to v2

See the [migration guide](MIGRATION.md).

## Contributing

Contributions are welcome and encouraged! If you'd like to contribute, send
us a [pull request] and refer to our [code of conduct] and [contributing guide].

## Terms of Service

This library uses Google Maps Platform services. Use of Google Maps
Platform services through this library is subject to the Google Maps
Platform [Terms of Service].

This library is not a Google Maps Platform Core Service. Therefore, the
Google Maps Platform Terms of Service (e.g. Technical Support Services,
Service Level Agreements, and Deprecation Policy) do not apply to the code
in this library.

### European Economic Area (EEA) developers

If your billing address is in the European Economic Area, effective on 8 July 2025, the [Google Maps Platform EEA Terms of Service](https://cloud.google.com/terms/maps-platform/eea) will apply to your use of the Services. Functionality varies by region. [Learn more](https://developers.google.com/maps/comms/eea/faq).

## Support

This library is offered via an open source [license]. It is not governed by
the Google Maps Platform Support [Technical Support Services Guidelines],
the [SLA], or the [Deprecation Policy]. However, any Google Maps Platform
services used by the library remain subject to the Google Maps Platform Terms of Service.

This library adheres to [semantic versioning] to indicate when
backwards-incompatible changes are introduced.

If you find a bug, or have a feature request, please [file an issue] on
GitHub. If you would like to get answers to technical questions from other
Google Maps Platform developers, ask through one of our
[developer community channels].
If you'd like to contribute, please check the [contributing guide].

You can also discuss this library on our [Discord server].

[API key]: https://developers.google.com/maps/documentation/javascript/get-api-key
[maps-sdk]: https://developers.google.com/maps/documentation/javascript
[reference]: https://googlemaps.github.io/js-api-loader/index.html
[documentation]: https://googlemaps.github.io/js-api-loader
[parameters]: https://developers.google.com/maps/documentation/javascript/load-maps-js-api#required_parameters
[npm-pkg]: https://npmjs.com/package/@googlemaps/js-api-loader
[code of conduct]: ?tab=coc-ov-file#readme
[contributing guide]: CONTRIBUTING.md
[Deprecation Policy]: https://cloud.google.com/maps-platform/terms
[developer community channels]: https://developers.google.com/maps/developer-community
[Discord server]: https://discord.gg/hYsWbmk
[file an issue]: https://github.com/googlemaps/js-api-loader/issues/new/choose
[license]: LICENSE
[project]: https://developers.google.com/maps/documentation/javascript/cloud-setup#enabling-apis
[pull request]: https://github.com/googlemaps/js-api-loader/compare
[semantic versioning]: https://semver.org
[Sign up with Google Maps Platform]: https://console.cloud.google.com/google/maps-apis/start
[SLA]: https://cloud.google.com/maps-platform/terms/sla
[Technical Support Services Guidelines]: https://cloud.google.com/maps-platform/terms/tssg
[Terms of Service]: https://cloud.google.com/maps-platform/terms