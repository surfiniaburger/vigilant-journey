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



Google Cloud Skills Boost
Dashboard
Explore
Paths
Subscriptions

Apply your skills in Google Cloud console

Deploy Multi-Agent Systems with Agent Development Kit (ADK) and Agent Engine
Course · 6 hours
10% complete
home
Course overview


Introduction
keyboard_arrow_right

Introducing Agent Development Kit
keyboard_arrow_right
youtube_tv
Introducing Agent Development Kit (ADK)
quiz
Module quiz

Develop agents with ADK
keyboard_arrow_right
youtube_tv
Develop agents with ADK
youtube_tv
Configure ADK
science
Get started with Agent Development Kit (ADK)
science
Empower ADK agents with tools
quiz
Module quiz

Build multi-agent systems with ADK
keyboard_arrow_right
youtube_tv
Build multi-agent systems with ADK
youtube_tv
Callbacks
science
Build Multi-Agent Systems with ADK
quiz
Module quiz

Deploy ADK agent to Agent Engine
keyboard_arrow_right
youtube_tv
Deploy Agent Development Kit agents to Agent Engine
science
Deploy ADK agents to Agent Engine
quiz
Module quiz

Extend agents with MCP and A2A
keyboard_arrow_right
science
Use Model Context Protocol (MCP) Tools with ADK Agents
science
Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK

Evaluate ADK agent systems
keyboard_arrow_right
Activity completed
check
youtube_tv
Evaluate and test ADK Agent Systems
science
Evaluate ADK agent performance using the Vertex AI Generative AI Evaluation Service
quiz
Module quiz

Your Next Steps
keyboard_arrow_right
Activity locked
lock
check_circle
Course Badge
Activity locked
lock
description
Course Survey
Course 
navigate_next
Extend agents with MCP and A2A 
navigate_next
—/100








Lab setup instructions and requirements
01:00:00
Lab instructions and tasks
GENAI120
Objectives
Setup and requirements
Task 1. Install ADK and set up your environment
Task 2. Explore the ADK agent you will make available remotely
Task 3. Deploy the agent as an A2A Server
Task 4. Enable another ADK agent to call this agent remotely
Congratulations!
Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK
experiment
Lab
schedule
1 hour
universal_currency_alt
7 Credits
show_chart
Advanced
info
This lab may incorporate AI tools to support your learning.
GENAI120
Google Cloud Self-Paced Labs

The Agent2Agent (A2A) protocol addresses a critical challenge in the AI landscape: enabling Gen AI agents, built on diverse frameworks by different companies running on separate servers, to communicate and collaborate effectively - as agents, not just as tools. A2A aims to provide a common language for agents, fostering a more interconnected, powerful, and innovative AI ecosystem.

A2A is built around a few core concepts that make it powerful and flexible:

Standardized Communication: JSON-RPC 2.0 over HTTP(S).
Agent Discovery: Agent Cards detail an agent's capabilities and connection info, so agents can discover each other and learn about each other's capabilities
Rich Data Exchange: Handles text, files, and structured JSON data.
Flexible Interaction: Supports synchronous request/response, streaming (SSE), and asynchronous push notifications.
Enterprise-Ready: Designed with security, authentication, and observability in mind.
Objectives
In this lab, you will:

Deploy an ADK agent as an A2A Server.
Prepare a JSON Agent Card to describe an A2A agent's capabilities.
Enable another ADK agent to read the Agent Card of your deployed A2A agent and use it as a sub-agent.
Setup and requirements
Before you click the Start Lab button
Read these instructions. Labs are timed and you cannot pause them. The timer, which starts when you click Start Lab, shows how long Google Cloud resources will be made available to you.

This Qwiklabs hands-on lab lets you do the lab activities yourself in a real cloud environment, not in a simulation or demo environment. It does so by giving you new, temporary credentials that you use to sign in and access Google Cloud for the duration of the lab.

What you need
To complete this lab, you need:

Access to a standard internet browser (Chrome browser recommended).
Time to complete the lab.
Note: If you already have your own personal Google Cloud account or project, do not use it for this lab.

Note: If you are using a Pixelbook, open an Incognito window to run this lab.

How to start your lab and sign in to the Google Cloud console
Click the Start Lab button. If you need to pay for the lab, a dialog opens for you to select your payment method. On the left is the Lab Details pane with the following:

The Open Google Cloud console button
Time remaining
The temporary credentials that you must use for this lab
Other information, if needed, to step through this lab
Click Open Google Cloud console (or right-click and select Open Link in Incognito Window if you are running the Chrome browser).

The lab spins up resources, and then opens another tab that shows the Sign in page.

Tip: Arrange the tabs in separate windows, side-by-side.

Note: If you see the Choose an account dialog, click Use Another Account.
If necessary, copy the Username below and paste it into the Sign in dialog.

"Username"
Copied!
You can also find the Username in the Lab Details pane.

Click Next.

Copy the Password below and paste it into the Welcome dialog.

"Password"
Copied!
You can also find the Password in the Lab Details pane.

Click Next.

Important: You must use the credentials the lab provides you. Do not use your Google Cloud account credentials.
Note: Using your own Google Cloud account for this lab may incur extra charges.
Click through the subsequent pages:

Accept the terms and conditions.
Do not add recovery options or two-factor authentication (because this is a temporary account).
Do not sign up for free trials.
After a few moments, the Google Cloud console opens in this tab.

Note: To access Google Cloud products and services, click the Navigation menu or type the service or product name in the Search field. Navigation menu icon and Search field
Task 1. Install ADK and set up your environment
In this lab environment, the Vertex AI API and Cloud Run API have been enabled for you. If you were to follow these steps in your own project, you would enable them by navigating to Vertex AI and following the prompt to enable it.

Prepare a Cloud Shell Editor tab
With your Google Cloud console window selected, open Cloud Shell by pressing the G key and then the S key on your keyboard. Alternatively, you can click the Activate Cloud Shell button (Activate Cloud Shell) in the upper right of the Cloud console.

Click Continue.

When prompted to authorize Cloud Shell, click Authorize.

In the upper right corner of the Cloud Shell Terminal panel, click the Open in new window button Open in new window button.

In the Cloud Shell Terminal, enter the following to open the Cloud Shell Editor to your home directory:

cloudshell workspace ~
Copied!
Close any additional tutorial or Gemini panels that appear on the right side of the screen to save more of your window for your code editor.

Throughout the rest of this lab, you can work in this window as your IDE with the Cloud Shell Editor and Cloud Shell Terminal.

Download and install the ADK and code samples for this lab
Install ADK by running the following command in the Cloud Shell Terminal. Note: You will specify the version to ensure that the version of ADK that you install corresponds to the version used in this lab:

# Install ADK and the A2A Python SDK
cd ~
export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install google-adk==1.8.0 a2a-sdk==0.2.16
pip install --upgrade google-genai
# Correcting a typo in this version
sed -i 's/{a2a_option}"/{a2a_option} "/' ~/.local/lib/python3.12/site-packages/google/adk/cli/cli_deploy.py
Copied!
Paste the following commands into the Cloud Shell Terminal to copy lab code from a Cloud Storage bucket and unzip it:

gcloud storage cp gs://YOUR_GCP_PROJECT_ID-bucket/adk_and_a2a.zip ./adk_and_a2a.zip
unzip adk_and_a2a.zip
Copied!
Click Check my progress to verify the objective.
Install ADK and set up your environment.

Task 2. Explore the ADK agent you will make available remotely
For the purposes of this lab, imagine you work for a stadium maintenance company: Cymbal Stadiums. As part of a recent project, you developed an image generation-agent that can create illustrations according to your brand guidelines. Now, several different teams in your organization want to use it too.

If you were to copy the code for use as a sub-agent by many agents, it would be very difficult to maintain and improve all of these copies.

Instead, you can deploy the agent once as an agent wrapped with an A2A server, and the other teams' agents can incorporate it by querying it remotely.

In the Cloud Shell Editor's file explorer pane, navigate to the adk_and_a2a/illustration_agent directory. This directory contains the ADK agent you will make available remotely. Click the directory to toggle it open.

Open the agent.py file on this directory and scroll to the section labeled # Tools.

Notice the generate_image() function, which will be used as a tool by this agent. It receives a prompt and performs a two-step process. First, it uses the Google Gen AI SDK to call generate_content(), which returns the raw image data directly in the response. Second, the function uses the Cloud Storage library to upload these image bytes to a GCS bucket. Finally, the tool returns the public URL of the newly created image file.

Notice that the instruction provided to the root_agent provides specific instructions to the agent to use image-generation prompts that respect the company's brand guidelines. For example, it specifies:

a specific illustration style: (Corporate Memphis)
a color palette (purples and greens on sunset gradients)
examples of stadium/sports and maintenance imagery because it is a stadium maintenance company
To see it in action, you'll first need to write a .env file to set environment variables needed by ADK agents. Run the following in the Cloud Shell Terminal to write this file in this directory.

cd ~/adk_and_a2a
cat << EOF > illustration_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID
GOOGLE_CLOUD_LOCATION=global
MODEL=gemini_flash_model_id
IMAGE_MODEL=gemini_flash_image_model_id
EOF
Copied!
Run the following to copy the .env to another agent directory you'll use in this lab:

cp illustration_agent/.env slide_content_agent/.env
Copied!
Now from the Cloud Shell Terminal, launch the ADK dev UI with:

adk web
Copied!
Output

INFO:     Started server process [2434]
INFO:     Waiting for application startup.
+-------------------------------------------------------+
| ADK Web Server started                                |
|                                                       |
| For local testing, access at http://localhost:8000.   |
+-------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit) 
To view the web interface in a new tab, click the http://127.0.0.1:8000 link at the bottom of the Terminal output.

A new browser tab will open with the ADK Dev UI.

From the Select an agent dropdown on the left, select the illustration_agent from the dropdown.

Query the agent with some text that could be used in a recruitment slide deck:

By supporting each other, we get big things done!
Copied!
After about 10 seconds, the agent should respond with the prompt it generated and a URL to preview the image. Click the image URL to preview the image, then click Back in your browser to return to the Dev UI.

Example Output

Example response from the model

Example Image

Generated image

Notice that the prompt you provided to the agent didn't mention sports, stadiums, or maintenance work, but the agent took your text and the brand guidelines and combined them into a single prompt for the image generation model.

When you are finished exploring the base agent, close the browser tab.

Click on the Cloud Shell Terminal pane and press CTRL + C to stop the server.

Click Check my progress to verify the objective.
Explore the ADK agent.

Task 3. Deploy the agent as an A2A Server
You'll now take the steps to deploy this agent as a remote A2A agent.

An A2A Agent identifies itself and its capabilities by serving an Agent Card. Run the following to create an agent.json file.

touch illustration_agent/agent.json
Copied!
Open the agent.json file within the adk_and_a2a/illustration_agent directory and paste in the following contents:

{
    "name": "illustration_agent",
    "description": "An agent designed to generate branded illustrations for Cymbal Stadiums.",
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["application/json"],
    "skills": [
    {
        "id": "illustrate_text",
        "name": "Illustrate Text",
        "description": "Generate an illustration to illustrate the meaning of provided text.",
        "tags": ["illustration", "image generation"]
    }
    ],
    "url": "https://illustration-agent-Project Number.GCP_LOCATION.run.app/a2a/illustration_agent",
    "capabilities": {},
    "version": "1.0.0"
}
Copied!
Save the file.

Review the JSON in the agent.json file. Notice that it gives the agent a name and description and identifies some skills . It also indicates a url where the agent itself can be called.

The agent's url is constructed to be its Cloud Run service URL once you have deployed it following the instructions in this lab.

While similar in name to skills, the parameter capabilities here is reserved to indicate abilities like streaming.

Run the following to create a requirements.txt file in the illustration_agent directory.

touch illustration_agent/requirements.txt
Copied!
Select the file, and paste the following into the file.

google-adk==1.8.0
a2a-sdk==0.2.16
Copied!
Save the file.

In the following command, you will use adk deploy cloud_run with the --a2a flag to deploy your agent to Cloud Run as an A2A server. You can learn more about deploying agents to Cloud Run by searching for the lab "Deploy ADK agents to Cloud Run". In this command:

the --project and --region define the project and region in which your Cloud Run service will be deployed
the --service_name defines the name for the Cloud Run service
the --a2a flag indicates it should be hosted as an A2A agent. This means two things:
your agent will be wrapped by a class which bridges ADK and A2A agents: the A2aAgentExecutor. This class translates A2A Protocol's language of tasks and messages to an ADK Runner in its language of events.
the Agent Card will be hosted as well at CLOUD_RUN_URL/a2a/AGENT_NAME/.well-known/agent.json. Note: While this version of the card will be usable soon, the dynamic rewriting of the agent's url currently does not work with Cloud Run, so we won't use it in this version of this lab.
Deploy the agent to Cloud Run as an A2A server with the following command:

adk deploy cloud_run \
    --project YOUR_GCP_PROJECT_ID \
    --region GCP_LOCATION \
    --service_name illustration-agent \
    --a2a \
    illustration_agent
Copied!
You will be prompted to allow unauthenticated responses for this container. For the sake of lab testing, enter Y into the Cloud Shell Terminal (for "yes") and press return.

Note: Deployment should take about 5-10 minutes. If you encounter a PERMISSION_DENIED error, try running the above command again.
Expected output:

You will see steps relating to building a Dockerfile and deploying the container, then deploying the service, followed by:

Service [illustration-agent] revision [illustration-agent-00001-xpp] has been deployed and is serving 100 percent of traffic.
Service URL: https://illustration-agent-Project Number.GCP_LOCATION.run.app
Click Check my progress to verify the objective.
Deploy the Agent as an A2A Server.

Task 4. Enable another ADK agent to call this agent remotely
In this task, you will provide a second ADK agent the ability to identify your illustration agent's capabilities and call it remotely. This second agent will be an agent tasked with creating contents for slides. It will write a headline and a couple of sentences of body text, then transfer to the illustration agent to generate an image to illustrate that text.

In the Cloud Shell Terminal, run the following command to copy the Agent Card JSON file to your adk_and_a2a directory and change its name to indicate that it represents the illustration_agent.

cp illustration_agent/agent.json illustration-agent-card.json
Copied!
In the Cloud Shell Editor's file explorer pane, navigate to the adk_and_a2a/slide_content_agent and open the agent.py file.

Review this agent's instruction to see it will take a user's suggestion for a slide and write a headline & body text, then transfer to your A2A agent to illustrate the slide.

Paste the following code under the # Agents header to add the remote agent using the RemoteA2aAgent class from ADK:

illustration_agent = RemoteA2aAgent(
    name="illustration_agent",
    description="Agent that generates illustrations.",
    agent_card=(
        "illustration-agent-card.json"
    ),
)
Copied!
Add the illustration_agent as a sub-agent of the root_agent by adding the following parameter to the root_agent:

sub_agents=[illustration_agent]
Copied!
Save the file.

Launch the UI from the Cloud Shell Terminal with:

cd ~/adk_and_a2a
adk web
Copied!
Once again, click the http://127.0.0.1:8000 link in the Terminal output.

A new browser tab will open with the ADK Dev UI. From the Select an agent dropdown on the left, select the slide_content_agent from the dropdown.

Query the agent with an idea for a slide:

Create content for a slide about our excellent on-the-job training.
Copied!
You should see the following output:

A headline and body text written by the slide_content_agent itself
A call to transfer_to_agent, indicating a transfer to the illustration_agent
The response from the illustration_agent with a link you can click on to see the new image.
The agent generates text, then transfers to the illustration_agent to generate an image.
Generated image

Click Check my progress to verify the objective.
Enable another ADK agent to call the agent remotely.

Congratulations!
In this lab, you’ve deployed an ADK agent as an A2A Server, prepared a JSON Agent Card to describe an A2A agent's capabilities, and enabled another ADK agent to read the Agent Card of your deployed A2A agent and use it as a sub-agent

Google Cloud training and certification
...helps you make the most of Google Cloud technologies. Our classes include technical skills and best practices to help you get up to speed quickly and continue your learning journey. We offer fundamental to advanced level training, with on-demand, live, and virtual options to suit your busy schedule. Certifications help you validate and prove your skill and expertise in Google Cloud technologies.

Manual Last Updated October 6, 2025

Lab Last Tested October 6, 2025

Copyright 2023 Google LLC All rights reserved. Google and the Google logo are trademarks of Google LLC. All other company and product names may be trademarks of the respective companies with which they are associated.







Could not connect to the reCAPTCHA service. Please check your internet connection and reload to get a reCAPTCHA challenge.


Google Cloud Skills Boost
Dashboard
Explore
Paths
Subscriptions

Apply your skills in Google Cloud console

Deploy Multi-Agent Systems with Agent Development Kit (ADK) and Agent Engine
Course · 6 hours
10% complete
home
Course overview


Introduction
keyboard_arrow_right

Introducing Agent Development Kit
keyboard_arrow_right
youtube_tv
Introducing Agent Development Kit (ADK)
quiz
Module quiz

Develop agents with ADK
keyboard_arrow_right
youtube_tv
Develop agents with ADK
youtube_tv
Configure ADK
science
Get started with Agent Development Kit (ADK)
science
Empower ADK agents with tools
quiz
Module quiz

Build multi-agent systems with ADK
keyboard_arrow_right
youtube_tv
Build multi-agent systems with ADK
youtube_tv
Callbacks
science
Build Multi-Agent Systems with ADK
quiz
Module quiz

Deploy ADK agent to Agent Engine
keyboard_arrow_right
youtube_tv
Deploy Agent Development Kit agents to Agent Engine
science
Deploy ADK agents to Agent Engine
quiz
Module quiz

Extend agents with MCP and A2A
keyboard_arrow_right
science
Use Model Context Protocol (MCP) Tools with ADK Agents
science
Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK

Evaluate ADK agent systems
keyboard_arrow_right
Activity completed
check
youtube_tv
Evaluate and test ADK Agent Systems
science
Evaluate ADK agent performance using the Vertex AI Generative AI Evaluation Service
quiz
Module quiz

Your Next Steps
keyboard_arrow_right
Activity locked
lock
check_circle
Course Badge
Activity locked
lock
description
Course Survey
Course 
navigate_next
Extend agents with MCP and A2A 
navigate_next
—/100




Lab setup instructions and requirements
01:00:00
Lab instructions and tasks
GENAI124
Overview
Objectives
Setup and requirements
Task 1. Install ADK and set up your environment
Task 2. Using Google Maps MCP server with ADK agents (ADK as an MCP client) in adk web
Task 3. Building an MCP server with ADK tools (MCP server exposing ADK)
Congratulations!
Use Model Context Protocol (MCP) Tools with ADK Agents
experiment
Lab
schedule
1 hour
universal_currency_alt
7 Credits
show_chart
Advanced
info
This lab may incorporate AI tools to support your learning.
GENAI124
Google Cloud Self-Paced Labs

Overview
In this lab, you will explore Model Context Protocol (MCP), an open standard that enables seamless integration between external services, data sources, tools, and applications. You will learn how to integrate MCP into your ADK agents, using tools provided by existing MCP servers to enhance your ADK workflows. Additionally, you will see how to expose ADK tools like load_web_page through a custom-built MCP server, enabling broader integration with MCP clients.

What is Model Context Protocol (MCP)?

Model Context Protocol (MCP) is an open standard designed to standardize how Large Language Models (LLMs) like Gemini and Claude communicate with external applications, data sources, and tools. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

MCP follows a client-server architecture, defining how data (resources), interactive templates (prompts), and actionable functions (tools) are exposed by an MCP server and consumed by an MCP client (which could be an LLM host application or an AI agent).

This lab covers two primary integration patterns:

Using existing MCP Servers within ADK: An ADK agent acts as an MCP client, leveraging tools provided by external MCP servers.
Exposing ADK Tools via an MCP Server: Building an MCP server that wraps ADK tools, making them accessible to any MCP client.
Objectives
In this lab, you learn how to:

Use an ADK agent as an MCP client to interact with tools from existing MCP servers.
Configure and deploy your own MCP server to expose ADK tools to other clients.
Connect ADK agents with external tools through standardized MCP communication.
Enable seamless interaction between LLMs and tools using Model Context Protocol.
Setup and requirements
Before you click the Start Lab button
Read these instructions. Labs are timed and you cannot pause them. The timer, which starts when you click Start Lab, shows how long Google Cloud resources will be made available to you.

This Qwiklabs hands-on lab lets you do the lab activities yourself in a real cloud environment, not in a simulation or demo environment. It does so by giving you new, temporary credentials that you use to sign in and access Google Cloud for the duration of the lab.

What you need
To complete this lab, you need:

Access to a standard internet browser (Chrome browser recommended).
Time to complete the lab.
Note: If you already have your own personal Google Cloud account or project, do not use it for this lab.

Note: If you are using a Pixelbook, open an Incognito window to run this lab.

How to start your lab and sign in to the Google Cloud console
Click the Start Lab button. If you need to pay for the lab, a dialog opens for you to select your payment method. On the left is the Lab Details pane with the following:

The Open Google Cloud console button
Time remaining
The temporary credentials that you must use for this lab
Other information, if needed, to step through this lab
Click Open Google Cloud console (or right-click and select Open Link in Incognito Window if you are running the Chrome browser).

The lab spins up resources, and then opens another tab that shows the Sign in page.

Tip: Arrange the tabs in separate windows, side-by-side.

Note: If you see the Choose an account dialog, click Use Another Account.
If necessary, copy the Username below and paste it into the Sign in dialog.

"Username"
Copied!
You can also find the Username in the Lab Details pane.

Click Next.

Copy the Password below and paste it into the Welcome dialog.

"Password"
Copied!
You can also find the Password in the Lab Details pane.

Click Next.

Important: You must use the credentials the lab provides you. Do not use your Google Cloud account credentials.
Note: Using your own Google Cloud account for this lab may incur extra charges.
Click through the subsequent pages:

Accept the terms and conditions.
Do not add recovery options or two-factor authentication (because this is a temporary account).
Do not sign up for free trials.
After a few moments, the Google Cloud console opens in this tab.

Note: To access Google Cloud products and services, click the Navigation menu or type the service or product name in the Search field. Navigation menu icon and Search field
Task 1. Install ADK and set up your environment
In this lab environment, the Vertex AI API, Routes API and Directions API have been enabled for you.

Prepare a Cloud Shell Editor tab
With your Google Cloud console window selected, open Cloud Shell by pressing the G key and then the S key on your keyboard. Alternatively, you can click the Activate Cloud Shell button (Activate Cloud Shell) in the upper right of the Cloud console.

Click Continue.

When prompted to authorize Cloud Shell, click Authorize.

In the upper right corner of the Cloud Shell Terminal panel, click the Open in new window button Open in new window button.

In the Cloud Shell Terminal, enter the following to open the Cloud Shell Editor to your home directory:

cloudshell workspace ~
Copied!
Close any additional tutorial or Gemini panels that appear on the right side of the screen to save more of your window for your code editor.

Throughout the rest of this lab, you can work in this window as your IDE with the Cloud Shell Editor and Cloud Shell Terminal.

Download and install ADK and code samples for this lab
Install ADK by running the following command in the Cloud Shell Terminal.

Note: You will specify the version to ensure that the version of ADK that you install corresponds to the version used in this lab. You can view the latest version number and release notes at the adk-python repo.
sudo python3 -m pip install google-adk==1.5.0
Copied!
Paste the following commands into the Cloud Shell Terminal to copy a file from a Cloud Storage bucket, and unzip it, creating a project directory with code for this lab:

gcloud storage cp gs://YOUR_GCP_PROJECT_ID-bucket/adk_mcp_tools.zip .
unzip adk_mcp_tools.zip
Copied!
Install additional lab requirements with:

python3 -m pip install -r adk_mcp_tools/requirements.txt
Copied!
Click Check my progress to verify the objective.
Install ADK and set up your environment

Task 2. Using Google Maps MCP server with ADK agents (ADK as an MCP client) in adk web
This section demonstrates how to integrate tools from an external Google Maps MCP server into your ADK agents. This is the most common integration pattern when your ADK agent needs to use capabilities provided by an existing service that exposes an MCP interface. You will see how the MCPToolset class can be directly added to your agent's tools list, enabling seamless connection to an MCP server, discovery of its tools, and making them available for your agent to use. These examples primarily focus on interactions within the adk web development environment.

MCPToolset
The MCPToolset class is ADK's primary mechanism for integrating tools from an MCP server. When you include an MCPToolset instance in your agent's tools list, it automatically handles the interaction with the specified MCP server. Here's how it works:

Connection Management: On initialization, MCPToolset establishes and manages the connection to the MCP server. This can be a local server process (using StdioServerParameters for communication over standard input/output) or a remote server (using SseServerParams for Server-Sent Events). The toolset also handles the graceful shutdown of this connection when the agent or application terminates.
Tool Discovery & Adaptation: Once connected, MCPToolset queries the MCP server for its available tools (via the list_tools MCP method). It then converts the schemas of these discovered MCP tools into ADK-compatible BaseTool instances.
Exposure to Agent: These adapted tools are then made available to your LlmAgent as if they were native ADK tools.
Proxying Tool Calls: When your LlmAgent decides to use one of these tools, MCPToolset transparently proxies the call (using the call_tool MCP method) to the MCP server, sends the necessary arguments, and returns the server's response back to the agent.
Filtering (Optional): You can use the tool_filter parameter when creating an MCPToolset to select a specific subset of tools from the MCP server, rather than exposing all of them to your agent.
Get API key and Enable APIs
In this sub-section, you will generate a new API key named GOOGLE_MAPS_API_KEY.

Open the browser tab displaying the Google Cloud Console (not your Cloud Shell Editor).

You can close the Cloud Shell Terminal pane on this browser tab for more console area.

Search for Credentials in the search bar at the top of the page. Select it from the results.

On the Credentials page, click + Create Credentials at the top of the page, then select API key.

The API key created dialog will display your newly created API key. Be sure to save this key locally for later use in the lab.

Click Close on the dialog box.

Your newly created key will be named API Key 1 by default. Select the key, rename it to GOOGLE_MAPS_API_KEY, and click Save.

Google Map Key

Define your Agent with an MCPToolset for Google Maps
In this sub-section, you will configure your agent to use the MCPToolset for Google Maps, enabling it to seamlessly provide directions and location-based information.

In the Cloud Shell Editor's file explorer pane, find the adk_mcp_tools folder. Click it to toggle it open.

Navigate to the directory adk_mcp_tools/google_maps_mcp_agent.

Paste the following command in a plain text file, then update the YOUR_ACTUAL_API_KEY value with the Google Maps API key you generated and saved in a previous step:

cd ~/adk_mcp_tools
cat << EOF > google_maps_mcp_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=Project
GOOGLE_CLOUD_LOCATION=Region
GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_API_KEY"
MODEL=gemini_flash_model_id
EOF
Copied!
Copy and paste the updated command to Cloud Shell Terminal to run it and write a .env file which will provide authentication details for this agent directory.

Copy the .env file to the other agent directory you will use in this lab by running the following command:

cp google_maps_mcp_agent/.env adk_mcp_server/.env
Copied!
Next, add the following code where indicated in the agent.py file to add the Google maps tool to your agent. This will allow your agent to use the MCPToolset for Google Maps to provide directions or location-based information.

tools=[
    MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "@modelcontextprotocol/server-google-maps",
            ],
            env={
                "GOOGLE_MAPS_API_KEY": google_maps_api_key
            }
        ),
        timeout=15,
        ),
    )
],
Copied!
From the adk_mcp_tools project directory, launch the Agent Development Kit Dev UI with the following command:

adk web
Copied!
Output:

INFO:     Started server process [2434]
INFO:     Waiting for application startup.
+----------------------------------------------------+
| ADK Web Server started                             |
|                                                    |
| For local testing, access at http://localhost:8000.|
+----------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
To view the web interface in a new tab, click the http://127.0.0.1:8000 link in the Terminal output.

A new browser tab will open with the ADK Dev UI. From the Select an agent dropdown on the left, select the google_maps_mcp_agent from the dropdown.

Start a conversation with the agent and run the following prompts:

Get directions from GooglePlex to SFO.
Copied!
Note: If your API call times out the first time you use it, click + New Session in the upper right of the ADK Dev UI and try again.
What's the route from Paris, France to Berlin, Germany?
Copied!
Output:

Agent Response

Click the agent icon next to the agent's chat bubble with a lightning bolt, which indicates a function call. This will open up the Event inspector for this event:

ADK Tool Call
Notice that agent graph indicates several different tools, identified by the wrench emoji (🔧). Even though you only imported one MCPToolset, that tool set came with the different tools you see listed here, such as maps_place_details and maps_directions.

The agent graph indicates several tools
On the Request tab, you can see the structure of the request. You can use the arrows at the top of the Event inspector to browse the agent's thoughts, function calls, and responses.

When you are finished asking questions of this agent, close the dev UI browser tab.

Go back to the Cloud Shell Terminal panel and press CTRL + C to stop the server.

Click Check my progress to verify the objective.
Create API key and deploy ADK agent

Task 3. Building an MCP server with ADK tools (MCP server exposing ADK)
In this section, you'll learn how to expose the ADK load_web_page tool through a custom-built MCP server. This pattern allows you to wrap existing ADK tools and make them accessible to any standard MCP client application.

Create the MCP Server Script and Implement Server Logic
Return to your Cloud Shell Editor tab and select the adk_mcp_tools/adk_mcp_server directory.

A Python file named adk_server.py has been prepared and commented for you. Take some time to review that file, reading the comments to understand how the code wraps a tool and serves it as an MCP server. Notice how it allows MCP clients to list available tools as well as invoke the ADK tool asynchronously, handling requests and responses in an MCP-compliant format.

Test the Custom MCP Server with an ADK Agent
Click on the agent.py file in the adk_mcp_server directory.

Update the path to your adk_server.py file.

/home/Username/adk_mcp_tools/adk_mcp_server/adk_server.py
Copied!
Next, add the following code where indicated in the agent.py file to add the MCPToolset to your agent. An ADK agent acts as a client to the MCP server. This ADK agent will use MCPToolset to connect to your adk_server.py script.

tools=[
    MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3", # Command to run your MCP server script
            args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # Argument is the path to the script
        ),
        timeout=15,
        ),
        tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded
    )
],
Copied!
To run the MCP server, start the adk_server.py script by running the following command in Cloud Shell Terminal:

python3 ~/adk_mcp_tools/adk_mcp_server/adk_server.py
Copied!
Output:

MCP Server

Open a new Cloud Shell Terminal tab by clicking the add-session-button button at the top of the Cloud Shell Terminal window.

In the Cloud Shell Terminal, from the adk_mcp_tools project directory, launch the Agent Development Kit Dev UI with the following command:

cd ~/adk_mcp_tools
adk web
Copied!
To view the web interface in a new tab, click the http://127.0.0.1:8000 link in the Terminal output.

From the Select an agent dropdown on the left, select the adk_mcp_server from the dropdown.

Query the agent with:

Load the content from https://example.com.
Copied!
Output:

Agent response

What happens here:

The ADK agent (web_reader_mcp_client_agent) uses the MCPToolset to connect to your adk_server.py.
The MCP server will receive the call_tool request, execute the ADK load_web_page tool, and return the result.
The ADK agent will then relay this information. You should see logs from both the ADK Web UI (and its terminal) and from your adk_server.py terminal in the Cloud Shell Terminal tab where it is running.
This demonstrates that ADK tools can be encapsulated within an MCP server, making them accessible to a broad range of MCP-compliant clients including ADK agents.

Congratulations!
At the end of this lab, you have learned how to integrate external Model Context Protocol (MCP) tools into your ADK agents using the MCPToolset class. You’ve discovered how to connect to an MCP server, use its tools within your agent, and expose ADK tools like load_web_page through a custom MCP server. These skills enable you to extend your ADK agents with powerful, external services, enhancing your web development workflows.

Manual Last Updated October 6, 2025

Lab Last Tested October 6, 2025

Copyright 2023 Google LLC All rights reserved. Google and the Google logo are trademarks of Google LLC. All other company and product names may be trademarks of the respective companies with which they are associated.

Sorry, Evaluate ADK agent performance using the Vertex AI Generative AI Evaluation Service is currently unavailable.

close







Could not connect to the reCAPTCHA service. Please check your internet connection and reload to get a reCAPTCHA challenge.

Google Cloud Skills Boost
Dashboard
Explore
Paths
Subscriptions

Apply your skills in Google Cloud console

Deploy Multi-Agent Systems with Agent Development Kit (ADK) and Agent Engine
Course · 6 hours
10% complete
home
Course overview


Introduction
keyboard_arrow_right

Introducing Agent Development Kit
keyboard_arrow_right
youtube_tv
Introducing Agent Development Kit (ADK)
quiz
Module quiz

Develop agents with ADK
keyboard_arrow_right
youtube_tv
Develop agents with ADK
youtube_tv
Configure ADK
science
Get started with Agent Development Kit (ADK)
science
Empower ADK agents with tools
quiz
Module quiz

Build multi-agent systems with ADK
keyboard_arrow_right
youtube_tv
Build multi-agent systems with ADK
youtube_tv
Callbacks
science
Build Multi-Agent Systems with ADK
quiz
Module quiz

Deploy ADK agent to Agent Engine
keyboard_arrow_right
youtube_tv
Deploy Agent Development Kit agents to Agent Engine
science
Deploy ADK agents to Agent Engine
quiz
Module quiz

Extend agents with MCP and A2A
keyboard_arrow_right
science
Use Model Context Protocol (MCP) Tools with ADK Agents
science
Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK

Evaluate ADK agent systems
keyboard_arrow_right
Activity completed
check
youtube_tv
Evaluate and test ADK Agent Systems
science
Evaluate ADK agent performance using the Vertex AI Generative AI Evaluation Service
quiz
Module quiz

Your Next Steps
keyboard_arrow_right
Activity locked
lock
check_circle
Course Badge
Activity locked
lock
description
Course Survey
Course 
navigate_next
Build multi-agent systems with ADK 
navigate_next
—/100








Lab setup instructions and requirements
01:30:00
Lab instructions and tasks
GENAI106
Overview
Objectives
Setup and requirements
Multi-Agent Systems
Task 1. Install ADK and set up your environment
Task 2. Explore transfers between parent, sub-agent, and peer agents
Task 3. Use session state to store and retrieve specific information
Workflow Agents
Task 4. Begin building a multi-agent system with a SequentialAgent
Task 5. Add a LoopAgent for iterative work
Task 6. Use a "fan out and gather" pattern for report generation with a ParallelAgent
Custom workflow agents
Congratulations!
Build Multi-Agent Systems with ADK
experiment
Lab
schedule
1 hour 30 minutes
universal_currency_alt
5 Credits
show_chart
Advanced
info
This lab may incorporate AI tools to support your learning.
GENAI106
Google Cloud Self-Paced Labs

Overview
This lab covers orchestrating multi-agent systems within the Google Agent Development Kit (Google ADK).

This lab assumes that you are familiar with the basics of ADK and tool use as covered in the labs:

Get started with Google Agent Development Kit (ADK)
Empower ADK agents with tools
Objectives
In this lab, you will:

Create multiple agents and relate them to one another with parent to sub-agent relationships.
Build content across multiple turns of conversation and multiple agents by writing to a session's state dictionary.
Instruct agents to read values from the session state to use as context for their responses.
Use workflow agents to pass the conversation between agents directly.
Setup and requirements
Before you click the Start Lab button
Read these instructions. Labs are timed and you cannot pause them. The timer, which starts when you click Start Lab, shows how long Google Cloud resources will be made available to you.

This Qwiklabs hands-on lab lets you do the lab activities yourself in a real cloud environment, not in a simulation or demo environment. It does so by giving you new, temporary credentials that you use to sign in and access Google Cloud for the duration of the lab.

What you need
To complete this lab, you need:

Access to a standard internet browser (Chrome browser recommended).
Time to complete the lab.
Note: If you already have your own personal Google Cloud account or project, do not use it for this lab.

Note: If you are using a Pixelbook, open an Incognito window to run this lab.

How to start your lab and sign in to the Google Cloud console
Click the Start Lab button. If you need to pay for the lab, a dialog opens for you to select your payment method. On the left is the Lab Details pane with the following:

The Open Google Cloud console button
Time remaining
The temporary credentials that you must use for this lab
Other information, if needed, to step through this lab
Click Open Google Cloud console (or right-click and select Open Link in Incognito Window if you are running the Chrome browser).

The lab spins up resources, and then opens another tab that shows the Sign in page.

Tip: Arrange the tabs in separate windows, side-by-side.

Note: If you see the Choose an account dialog, click Use Another Account.
If necessary, copy the Username below and paste it into the Sign in dialog.

"Username"
Copied!
You can also find the Username in the Lab Details pane.

Click Next.

Copy the Password below and paste it into the Welcome dialog.

"Password"
Copied!
You can also find the Password in the Lab Details pane.

Click Next.

Important: You must use the credentials the lab provides you. Do not use your Google Cloud account credentials.
Note: Using your own Google Cloud account for this lab may incur extra charges.
Click through the subsequent pages:

Accept the terms and conditions.
Do not add recovery options or two-factor authentication (because this is a temporary account).
Do not sign up for free trials.
After a few moments, the Google Cloud console opens in this tab.

Note: To access Google Cloud products and services, click the Navigation menu or type the service or product name in the Search field. Navigation menu icon and Search field
Multi-Agent Systems
The Agent Development Kit empowers developers to get more reliable, sophisticated, multi-step behaviors from generative models. Instead of writing long, complex prompts that may not deliver results reliably, you can construct a flow of multiple, simple agents that can collaborate on complex problems by dividing tasks and responsibilities.

This architectural approach offers several key advantages such as:

Easier to design: You can think in terms of agents with specific jobs and skills.
Specialized functions with more reliable performance: Specialized agents can learn from clear examples to become more reliable at their specific tasks.
Organization: Dividing the workflow into distinct agents allows for a more organized, and therefor easier to think about, approach.
Improvability and maintainability: It is easier to improve or fix a specialized component rather than make changes to a complex agent that may fix one behavior but might impact others.
Modularity: Distinct agents from one workflow can be easily copied and included in other similar workflows.
The Hierarchical Agent Tree
Tree structure showing hierarchical agents

In Agent Development Kit, you organize your agents in a tree-like structure. This helps limit the options for transfers for each agent in the tree, making it easier to control and predict the possible routes the conversation can take through the tree. Benefits of the hierarchical structure include:

It draws inspiration from real-world collaborative teams, making it easier to design and reason about the behavior of the multi-agent system.
It is intuitive for developers, as it mirrors common software development patterns.
It provides greater control over the flow of information and task delegation within the system, making it easier to understand possible pathways and debug the system. For example, if a system has two report-generation agents at different parts of its flow with similar descriptions, the tree structure makes it easier to ensure that the correct one is invoked.
The structure always begins with the agent defined in the root_agent variable (although it may have a different user-facing name to identify itself). The root_agent may act as a parent to one or more sub-agents. Each sub-agent agent may have its own sub-agents.

Task 1. Install ADK and set up your environment
In this lab environment, the Vertex AI API has been enabled for you. If you were to follow these steps in your own project, you would enable it by navigating to Vertex AI and following the prompt to enable it.

Prepare a Cloud Shell Editor tab
With your Google Cloud console window selected, open Cloud Shell by pressing the G key and then the S key on your keyboard. Alternatively, you can click the Activate Cloud Shell button (Activate Cloud Shell) in the upper right of the Cloud console.

Click Continue.

When prompted to authorize Cloud Shell, click Authorize.

In the upper right corner of the Cloud Shell Terminal panel, click the Open in new window button Open in new window button.

In the Cloud Shell Terminal, enter the following to open the Cloud Shell Editor to your home directory:

cloudshell workspace ~
Copied!
Close any additional tutorial or Gemini panels that appear on the right side of the screen to save more of your window for your code editor.
Throughout the rest of this lab, you can work in this window as your IDE with the Cloud Shell Editor and Cloud Shell Terminal.
Download and install ADK and code samples for this lab
Paste the following commands into the Cloud Shell Terminal to copy code files from a Cloud Storage bucket for this lab:

gcloud storage cp -r gs://YOUR_GCP_PROJECT_ID-bucket/adk_multiagent_systems .
Copied!
Update your PATH environment variable, install ADK, and install additional lab requirements by running the following commands in the Cloud Shell Terminal.

export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install google-adk -r adk_multiagent_systems/requirements.txt
Copied!
Task 2. Explore transfers between parent, sub-agent, and peer agents
The conversation always begins with the agent defined as the root_agent variable.

The default behavior of a parent agent is to understand the description of each sub-agent and determine if control of the conversation should be transferred to a sub-agent at any point.

You can help guide those transfers in the parent's instruction by referring to the sub-agents by name (the values of their name parameter, not their variable names). Try an example:

In the Cloud Shell Terminal, run the following to create a .env file to authenticate the agent in the parent_and_subagents directory.

cd ~/adk_multiagent_systems
cat << EOF > parent_and_subagents/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID
GOOGLE_CLOUD_LOCATION=global
MODEL=gemini_flash_model_id
EOF
Copied!
Run the following command to copy that .env file to the workflow_agents directory, which you will use later in the lab:

cp parent_and_subagents/.env workflow_agents/.env
Copied!
In the Cloud Shell Editor file explorer pane, navigate to the adk_multiagent_systems/parent_and_subagents directory.

Click on the agent.py file to open it.

Tip: Because Python code requires that we define our sub-agents before we can add them to an agent, in order to read an agent.py file in the order of the conversation flow, you may want to start reading with the bottom agent and work back towards the top.
Notice that there are three agents here:

a root_agent named steering (its name is used to identify it in ADK's dev UI and command line interfaces). It asks the user a question (if they know where they'd like to travel or if they need some help deciding), and the user's response to that question will help this steering agent know which of its two sub-agents to steer the conversation towards. Notice that it only has a simple instruction that does not mention the sub-agents, but it is aware of its sub-agents' descriptions.
a travel_brainstormer that helps the user brainstorm destinations if they don't know where they would like to visit.
an attractions_planner that helps the user build a list of things to do once they know which country they would like to visit.
Make travel_brainstormer and attractions_planner sub-agents of the root_agent by adding the following line to the creation of the root_agent:

sub_agents=[travel_brainstormer, attractions_planner]
Copied!
Save the file.

Note that you don't add a corresponding parent parameter to the sub-agents. The hierarchical tree is defined only by specifying sub_agents when creating parent agents.

In the Cloud Shell Terminal, run the following to use the ADK command line interface to chat with your agent:

cd ~/adk_multiagent_systems
adk run parent_and_subagents
Copied!
When you are presented the [user]: prompt, greet the agent with:

hello
Copied!
Example output (yours may be a little different):

user: hello
[steering]: Hi there! Do you already have a country in mind for your trip, or would you like some help deciding where to go?
Tell the agent:

I could use some help deciding.
Copied!
Example output (yours may be a little different):

user: I could use some help deciding.
[travel_brainstormer]: Okay! To give you the best recommendations, I need to understand what you're looking for in a trip.
...
Notice from the name [travel_brainstormer] in brackets in the response that the root_agent (named [steering]) has transferred the conversation to the appropriate sub-agent based on that sub-agent's description alone.

At the user: prompt, enter exit to end the conversation.

You can also provide your agent more detailed instructions about when to transfer to a sub-agent as part of its instructions. In the agent.py file, add the following lines to the root_agent's instruction:

If they need help deciding, send them to
'travel_brainstormer'.
If they know what country they'd like to visit,
send them to the 'attractions_planner'.
Copied!
Save the file.

In the Cloud Shell Terminal, run the following to start the command line interface again:

adk run parent_and_subagents
Copied!
Greet the agent with:

hello
Copied!
Reply to the agent's greeting with:

I would like to go to Japan.
Copied!
Example output (yours may be a little different):

user: I would like to go to Japan.
[attractions_planner]: Okay, I can help you with that! Here are some popular attractions in Japan:

*   **Tokyo:**
    *   Senso-ji Temple
    *   Shibuya Crossing
    *   Tokyo Skytree
*   **Kyoto:**
    ...
Notice that you have been transferred to the other sub-agent, attractions_planner.

Reply with:

Actually I don't know what country to visit.
Copied!
Example output (yours may be a little different):

user: actually I don't know what country to visit
[travel_brainstormer]: Okay! I can help you brainstorm some countries for travel...
Notice you have been transferred to the travel_brainstormer agent, which is a peer agent to the attractions_planner. This is allowed by default. If you wanted to prevent transfers to peers, you could have set the disallow_transfer_to_peers parameter to True on the attractions_planner agent.

At the user prompt, type exit to end the session.

Step-by-step pattern: If you are interested in an agent that guides a user through a process step-by-step, one useful pattern can be to make the first step the root_agent with the second step agent its only sub-agent, and continue with each additional step being the only sub-agent of the previous step's agent.
Click Check my progress to verify the objective.
Explore transfers between parent, sub-agent, and peer agents

Task 3. Use session state to store and retrieve specific information
Each conversation in ADK is contained within a Session that all agents involved in the conversation can access. A session includes the conversation history, which agents read as part of the context used to generate a response. The session also includes a session state dictionary that you can use to take greater control over the most important pieces of information you would like to highlight and how they are accessed.

This can be particularly helpful to pass information between agents or to maintain a simple data structure, like a list of tasks, over the course of a conversation with a user.

To explore adding to and reading from state:

Return to the file adk_multiagent_systems/parent_and_subagents/agent.py

Paste the following function definition after the # Tools header:

def save_attractions_to_state(
    tool_context: ToolContext,
    attractions: List[str]
) -> dict[str, str]:
    """Saves the list of attractions to state["attractions"].

    Args:
        attractions [str]: a list of strings to add to the list of attractions

    Returns:
        None
    """
    # Load existing attractions from state. If none exist, start an empty list
    existing_attractions = tool_context.state.get("attractions", [])

    # Update the 'attractions' key with a combo of old and new lists.
    # When the tool is run, ADK will create an event and make
    # corresponding updates in the session's state.
    tool_context.state["attractions"] = existing_attractions + attractions

    # A best practice for tools is to return a status message in a return dict
    return {"status": "success"}
Copied!
In this code, notice:

The session is passed to your tool function as ToolContext. All you need to do is assign a parameter to receive it, as you see here with the parameter named tool_context. You can then use tool_context to access session information like conversation history (through tool_context.events) and the session state dictionary (through tool_context.state). When the tool_context.state dictionary is modified by your tool function, those changes will be reflected in the session's state after the tool finishes its execution.
The docstring provides a clear description and sections for argument and return values.
The commented function code demonstrates how easy it is to make updates to the state dictionary.
Add the tool to the attractions_planner agent by adding the tools parameter when the agent is created:

tools=[save_attractions_to_state]
Copied!
Add the following bullet points to the attractions_planner agent's existing instruction:

- When they reply, use your tool to save their selected attraction
and then provide more possible attractions.
- If they ask to view the list, provide a bulleted list of
{ attractions? } and then suggest some more.
Copied!
Notice the section in curly braces: { attractions? }. This ADK feature, key templating, loads the value of the attractions key from the state dictionary. The question mark after the attractions key prevents this from erroring if the field is not yet present.

You will now run the agent from the web interface, which provides a tab for you to see the changes being made to the session state. Launch the Agent Development Kit Web UI with the following command:

adk web
Copied!
Output

INFO:     Started server process [2434]
INFO:     Waiting for application startup.
+-------------------------------------------------------+
| ADK Web Server started                                |
|                                                       |
| For local testing, access at http://localhost:8000.   |
+-------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit) 
To view the web interface in a new tab, click the http://127.0.0.1:8000 link in the Terminal output.

A new browser tab will open with the ADK Dev UI.

From the Select an agent dropdown on the left, select the parent_and_subagents agent from the dropdown.

Start the conversation with: hello

After the agent greets you, reply with:

I'd like to go to Egypt.
Copied!
You should be transferred to the attractions_planner and be provided a list of attractions.

Choose an attraction, for example:

I'll go to the Sphinx
Copied!
You should receive an acknowledgement in the response, like: Okay, I've saved The Sphinx to your list. Here are some other attractions...

Click the response tool box (marked with a check mark) to view the event created from the tool's response. Notice that it includes an actions field which includes state_delta describing the changes to the state.

You should be prompted by the agent to select more attractions. Reply to the agent by naming one of the options it has presented.

On the left-hand navigation menu, click the "X" to exit the focus on the event you inspected earlier.

Now in the sidebar, you should see the list of events and a few tab options. Select the State tab. Here you can view the current state, including your attractions array with the two values you have requested.

Session State preview in the Web UI

Send this message to the agent:

What is on my list?
Copied!
It should return your list formatted as a bulleted list according to its instruction.

When you are finished experimenting with the agent, close the web browser tab and press CTRL + C in the Cloud Shell Terminal to stop the server.

Later in this lab, you will demonstrate how to use state to communicate between agents.

Click Check my progress to verify the objective.
Use session state to store and retrieve specific information

Instead of saving small pieces of information, if you would like to store your agent's entire text response in the state dictionary, you can set an output_key parameter when you define the agent, and its entire output will be stored in the state dictionary under that field name.
Workflow Agents
Parent to sub-agent transfers are ideal when you have multiple specialist sub-agents, and you want the user to interact with each of them.

However, if you would like agents to act one-after-another without waiting for a turn from the user, you can use workflow agents. Some example scenarios when you might use workflow agents include when you would like your agents to:

Plan and Execute: When you want to have one agent prepare a list of items, and then have other agents use that list to perform follow-up tasks, for example writing sections of a document
Research and Write: When you want to have one agent call functions to collect contextual information from Google Search or other data sources, then another agent use that information to produce some output.
Draft and Revise: When you want to have one agent prepare a draft of a document, and then have other agents check the work and iterate on it
To accomplish these kinds of tasks, workflow agents have sub-agents and guarantee that each of their sub-agents acts. Agent Development Kit provides three built-in workflow agents and the opportunity to define your own:

SequentialAgent
LoopAgent
ParallelAgent
Throughout the rest of this lab, you will build a multi-agent system that uses multiple LLM agents, workflow agents, and tools to help control the flow of the agent.

Specifically, you will build an agent that will develop a pitch document for a new hit movie: a biographical film based on the life of a historical character. Your sub-agents will handle the research, an iterative writing loop with a screenwriter and a critic, and finally some additional sub-agents will help brainstorm casting ideas and use historical box office data to make some predictions about box office results.

In the end, your multi-agent system will look like this (you can click on the image to see it larger):

Diagram of a film_concept_team multi-agent system

But you will begin with a simpler version.

Task 4. Begin building a multi-agent system with a SequentialAgent
The SequentialAgent executes its sub-agents in a linear sequence. Each sub-agent in its sub_agents list is run, one after the other, in the order they are defined.

This is ideal for workflows where tasks must be performed in a specific order, and the output of one task serves as the input for the next.

In this task, you will run a SequentialAgent to build a first version of your movie pitch-development multi-agent system. The first draft of your agent will be structured like this:

Film_concept_team multi-agent system step 1

A root_agent named greeter to welcome the user and request a historical character as a movie subject

A SequentialAgent called film_concept_team will include:

A researcher to learn more about the requested historical figure from Wikipedia, using a LangChain tool covered in the lab Empower ADK agents with tools. An agent can choose to call its tool(s) multiple times in succession, so the researcher can take multiple turns in a row if it determines it needs to do more research.
A screenwriter to turn the research into a plot outline.
A file_writer to title the resulting movie and write the results of the sequence to a file.
In the Cloud Shell Editor, navigate to the directory adk_multiagent_systems/workflow_agents.

Click on the agent.py file in the workflow_agents directory.

Read through this agent definition file. Because sub-agents must be defined before they can be assigned to a parent, to read the file in the order of the conversational flow, you can read the agents from the bottom of the file to the top.

You also have a function tool append_to_state. This function allows agents with the tool the ability to add content to a dictionary value in state. It is particularly useful for agents that might call a tool multiple times or act in multiple passes of a LoopAgent, so that each time they act their output is stored.

Try out the current version of the agent by launching the web interface from the Cloud Shell Terminal. You will use the --reload_agents argument to enable live reloading of agents based on agent changes:

cd ~/adk_multiagent_systems
adk web --reload_agents
Copied!
Note: If you did not shut down your previous adk web session, the default port of 8000 will be blocked, but you can launch the Dev UI with a new port by using adk web --port 8001, for example.
To view the web interface in a new tab, click the http://127.0.0.1:8000 link in the Terminal output.

A new browser tab will open with the ADK Dev UI.

From the Select an agent dropdown on the left, select workflow_agents.

Start the conversation with: hello. It may take a few moments for the agent to respond, but it should request you enter a historical figure to start your film plot generation.

When prompted to enter a historical figure, you can enter one of your choice or use one of these examples:

Zhang Zhongjing - a renowned Chinese physician from the 2nd Century CE.
Ada Lovelace - an English mathematician and writer known for her work on early computers
Marcus Aurelius - a Roman emperor known for his philosophical writings.
The agent should now call its agents one after the other as it executes the workflow and writes the plot outline file to your ~/adk_multiagent_systems/movie_pitches directory. It should inform you when it has written the file to disk.

If you don't see the agent reporting that it generated a file for you or want to try another character, you can click + New Session in the upper right and try again.

View the agent's output in the Cloud Shell Editor. (You may need to use the Cloud Shell Editor's menu to enable View > Word Wrap to see the full text without lots of horizontal scrolling.)

In the ADK Dev UI, click on one of the agent icons (agent_icon) representing a turn of conversation to bring up the event view.

The event view provides a visual representation of the tree of agents and tools used in this session. You may need to scroll in the event panel to see the full plot.

adk web graph

In addition to the graph view, you can click on the Request tab of the event to see the information this agent received as part of its request, including the conversation history.
You can also click on the Response tab of the event to see what the agent returned.
Note: While this system can produce interesting results, it is not intended to imply that instructions can be so brief or adding examples can be skipped. The system's reliability would benefit greatly from the additional layer of adding more rigorous instructions and examples for each agent.
Click Check my progress to verify the objective.
Begin building a multi-agent system with a SequentialAgent

Task 5. Add a LoopAgent for iterative work
The LoopAgent executes its sub-agents in a defined sequence and then starts at the beginning of the sequence again without breaking for a user input. It repeats the loop until a number of iterations has been reached or a call to exit the loop has been made by one of its sub-agents (usually by calling a built-in exit_loop tool).

This is beneficial for tasks that require continuous refinement, monitoring, or cyclical workflows. Examples include:

Iterative Refinement: Continuously improve a document or plan through repeated agent cycles.
Continuous Monitoring: Periodically check data sources or conditions using a sequence of agents.
Debate or Negotiation: Simulate iterative discussions between agents to reach a better outcome.
You will add a LoopAgent to your movie pitch agent to allow multiple rounds of research and iteration while crafting the story. In addition to refining the script, this allows a user to start with a less specific input: instead of suggesting a specific historical figure, they might only know they want a story about an ancient doctor, and a research-and-writing iteration loop will allow the agents to find a good candidate, then work on the story.

Film_concept_team multi-agent system step 2

Your revised agent will flow like this:

The root_agent greeter will remain the same.
The film_concept_team SequentialAgent will now consist of:
A writers_room LoopAgent that will begin the sequence. It will consist of:
The researcher will be the same as before.
The screenwriter will be similar to before.
A critic that will offer critical feedback on the current draft to motivate the next round of research and improvement through the loop.
When the loop terminates, it will escalate control of the conversation back to the film_concept_team SequentialAgent, which will then pass control to the next agent in its sequence: the file_writer that will remain as before to give the movie a title and write the results of the sequence to a file.
To make these changes:

In the adk_multiagent_systems/workflow_agents/agent.py file, add this tool import so that you can provide an agent the ability to exit the loop when desired:

from google.adk.tools import exit_loop
Copied!
To determine when to exit the loop, add this critic agent to decide when the plot outline is ready. Paste the following new agent into the agent.py file under the # Agents section header (without overwriting the existing agents). Note that it has the exit_loop tool as one of its tools and instructions on when to use it:

critic = Agent(
    name="critic",
    model=model_name,
    description="Reviews the outline so that it can be improved.",
    instruction="""
    INSTRUCTIONS:
    Consider these questions about the PLOT_OUTLINE:
    - Does it meet a satisfying three-act cinematic structure?
    - Do the characters' struggles seem engaging?
    - Does it feel grounded in a real time period in history?
    - Does it sufficiently incorporate historical details from the RESEARCH?

    If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.
    If significant improvements can be made, use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
    Explain your decision and briefly summarize the feedback you have provided.

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    RESEARCH:
    { research? }
    """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[append_to_state, exit_loop]
)
Copied!
Create a new LoopAgent called writers_room that creates the iterative loop of the researcher, screenwriter, and critic. Each pass through the loop will end with a critical review of the work so far, which will prompt improvements for the next round. Paste the following above the existing film_concept_team SequentialAgent.

writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve a movie plot outline.",
    sub_agents=[
        researcher,
        screenwriter,
        critic
    ],
    max_iterations=5,
)
Copied!
Note that the LoopAgent creation includes a parameter for max_iterations. This defines how many times the loop will run before it ends. Even if you plan to interrupt the loop via another method, it is a good idea to include a cap on the total number of iterations.

Update the film_concept_team SequentialAgent to replace the researcher and screenwriter with the writers_room LoopAgent you just created. The file_writer agent should remain at the end of the sequence. The film_concept_team should now look like this:

film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[
        writers_room,
        file_writer
    ],
)
Copied!
Return to the ADK Dev UI tab and click the + New Session button in the upper right to start a new session.

Begin a new conversation with: hello

When prompted to choose a kind of historical character, choose one that interests you. Some ideas include:

an industrial designer who made products for the masses
a cartographer (a map maker)
that guy who made crops yield more food
Once you have chosen a type of character, the agent should work its way through iterations of the loop and finally give the film a title and write the outline to a file.

Using the Cloud Shell Editor, review the file generated, which should be saved in the adk_multiagent_systems/movie_pitches directory. (Once again, you may need to use the Editor's menu to enable View > Word Wrap to see the full text without lots of horizontal scrolling.)

Click Check my progress to verify the objective.
Add a LoopAgent for iterative work

Task 6. Use a "fan out and gather" pattern for report generation with a ParallelAgent
The ParallelAgent enables concurrent execution of its sub-agents. Each sub-agent operates in its own branch, and by default, they do not share conversation history or state directly with each other during parallel execution.

This is valuable for tasks that can be divided into independent sub-tasks that can be processed simultaneously. Using a ParallelAgent can significantly reduce the overall execution time for such tasks.

In this lab, you will add some supplemental reports -- some research on potential box office performance and some initial ideas on casting -- to enhance the pitch for your new film.

Film_concept_team multi-agent system step 3

Your revised agent will flow like this:

The greeter will the same.
The film_concept_team SequentialAgent will now consist of:
The writers_room LoopAgent, which will remain the same including:
The researcher agent
The screenwriter agent
The critic agent
Your new preproduction_team ParallelAgent will then act, consisting of:
A box_office_researcher agent to use historical box office data to generate a report on potential box office performance for this film
A casting_agent agent to generate some initial ideas on casting based on actors who have starred in similar films
The file_writer that will remain as before to write the results of the sequence to a file.
While much of this example demonstrates creative work that would be done by human teams, this workflow represents how a complex chain of tasks can be broken across several sub-agents to produce drafts of complex documents which human team members can then edit and improve upon.

Paste the following new agents and ParallelAgent into your workflow_agents/agent.py file under the # Agents header:

box_office_researcher = Agent(
    name="box_office_researcher",
    model=model_name,
    description="Considers the box office potential of this film",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    Write a report on the box office potential of a movie like that described in PLOT_OUTLINE based on the reported box office performance of other recent films.
    """,
    output_key="box_office_report"
)

casting_agent = Agent(
    name="casting_agent",
    model=model_name,
    description="Generates casting ideas for this film",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    Generate ideas for casting for the characters described in PLOT_OUTLINE
    by suggesting actors who have received positive feedback from critics and/or
    fans when they have played similar roles.
    """,
    output_key="casting_report"
)

preproduction_team = ParallelAgent(
    name="preproduction_team",
    sub_agents=[
        box_office_researcher,
        casting_agent
    ]
)
Copied!
Update the existing film_concept_team agent's sub_agents list to include the preproduction_team between the writers_room and file_writer:

film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[
        writers_room,
        preproduction_team,
        file_writer
    ],
)
Copied!
Update the file_writer's instruction to:

INSTRUCTIONS:
- Create a marketable, contemporary movie title suggestion for the movie described in the PLOT_OUTLINE. If a title has been suggested in PLOT_OUTLINE, you can use it, or replace it with a better one.
- Use your 'write_file' tool to create a new txt file with the following arguments:
    - for a filename, use the movie title
    - Write to the 'movie_pitches' directory.
    - For the 'content' to write, include:
        - The PLOT_OUTLINE
        - The BOX_OFFICE_REPORT
        - The CASTING_REPORT

PLOT_OUTLINE:
{ PLOT_OUTLINE? }

BOX_OFFICE_REPORT:
{ box_office_report? }

CASTING_REPORT:
{ casting_report? }
Copied!
Save the file.

In the ADK Dev UI, click + New Session in the upper right.

Enter hello to start the conversation.

When prompted, enter a new character idea that you are interested in. Some ideas include:

that actress who invented the technology for wifi
an exciting chef
key players in the worlds fair exhibitions
When the agent has completed its writing and report-generation, inspect the file it produced in the adk_multiagent_systems/movie_pitches directory. If a part of the process fails, click + New session in the upper right and try again.

Custom workflow agents
When the pre-defined workflow agents of SequentialAgent, LoopAgent, and ParallelAgent are insufficient for your needs, CustomAgent provides the flexibility to implement new workflow logic. You can define patterns for flow control, conditional execution, or state management between sub-agents. This is useful for complex workflows, stateful orchestrations, or integrating custom business logic into the framework's orchestration layer.

Creation of a CustomAgent is out of the scope of this lab, but it is good to know that it exists if you need it!

Congratulations!
In this lab, you’ve learned to create multiple agents and relate them to one another with parent to sub-agent relationships, add to the session state and read it in agent instructions, and use workflow agents to pass the conversation between agents directly.

Google Cloud training and certification
...helps you make the most of Google Cloud technologies. Our classes include technical skills and best practices to help you get up to speed quickly and continue your learning journey. We offer fundamental to advanced level training, with on-demand, live, and virtual options to suit your busy schedule. Certifications help you validate and prove your skill and expertise in Google Cloud technologies.

Manual Last Updated October 6, 2025

Lab Last Tested October 6, 2025

Copyright 2023 Google LLC All rights reserved. Google and the Google logo are trademarks of Google LLC. All other company and product names may be trademarks of the respective companies with which they are associated.







Could not connect to the reCAPTCHA service. Please check your internet connection and reload to get a reCAPTCHA challenge.


Skip to main content
Build and deploy an ADK agent that uses an MCP server on Cloud Run
access_time
52 mins remaining

English
Introduction
Why deploy to Cloud Run?
Setup and Requirements
Before you begin
Create the project folder
Create Agent Workflow
Prepare the application for deployment
Deploy the agent using the ADK CLI
Test the deployed agent
Clean up environment
Congratulations
Survey
6. Create Agent Workflow
Create init.py file
Create the init.py file. This file tells Python that the zoo_guide_agent directory is a package.


cloudshell edit __init__.py
The above command opens up the code editor. Add the following code to __init__.py:


from . import agent
Create main agent.py file
Create the main agent.py file. This command creates the Python file and pastes in the complete code for your multi-agent system.


cloudshell edit agent.py
Step 1: Imports and Initial Setup
This first block brings in all the necessary libraries from the ADK and Google Cloud. It also sets up logging and loads the environment variables from your .env file, which is crucial for accessing your model and server URL.

Add the following code to your agent.py file:


import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")
Step 2: Defining the Tools (The Agent's Capabilities)
3eb9c6772576b906.jpeg

An agent is only as good as the tools it can use. In this section, we define all the capabilities our agent will have, including a custom function to save data, an MCP Tool that connects to our secure MCP server along with a Wikipedia Tool.

Add the following code to the bottom of agent.py:


# Greet user and save their prompt

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}


# Configuring the MCP Tool to connect to the Zoo MCP server

mcp_server_url = os.getenv("MCP_SERVER_URL")
if not mcp_server_url:
    raise ValueError("The environment variable MCP_SERVER_URL is not set.")

def get_id_token():
    """Get an ID token to authenticate with the MCP server."""
    target_url = os.getenv("MCP_SERVER_URL")
    audience = target_url.split('/mcp/')[0]
    request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(request, audience)
    return id_token

"""
# Use this code if you are using the public MCP Server and comment out the code below defining mcp_tools
mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url
    )
)
"""

mcp_tools = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=mcp_server_url,
                headers={
                    "Authorization": f"Bearer {get_id_token()}",
                },
            ),
        )

# Configuring the Wikipedia Tool
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)
The Three Tools Explained

add_prompt_to_state 📝
This tool remembers what a zoo visitor asks. When a visitor asks, "Where are the lions?", this tool saves that specific question into the agent's memory so the other agents in the workflow know what to research.

How: It's a Python function that writes the visitor's prompt into the shared tool_context.state dictionary. This tool context represents the agent's short-term memory for a single conversation. Data saved to the state by one agent can be read by the next agent in the workflow.

MCPToolset 🦁
This is used to connect the tour guide agent to the zoo MCP server created in Lab 1. This server has special tools for looking up specific information about our animals, like their name, age, and enclosure.

How: It securely connects to the zoo's private server URL. It uses get_id_token to automatically get a secure "keycard" (a service account ID token) to prove its identity and gain access.

LangchainTool 🌍
This gives the tour guide agent general world knowledge. When a visitor asks a question that isn't in the zoo's database, like "What do lions eat in the wild?", this tool lets the agent look up the answer on Wikipedia.

How: It acts as an adapter, allowing our agent to use the pre-built WikipediaQueryRun tool from the LangChain library.

Resources:

MCP Toolset
Function Tools
State
Step 3: Defining the Specialist Agents
b8a9504b21920969.jpeg
Next we will define the researcher agent and response formatter agent. The researcher agent is the "brain" of our operation. This agent takes the user's prompt from the shared State, examines its powerful tools (the Zoo's MCP Server Tool and the Wikipedia Tool), and decides which ones to use to find the answer.

The response formatter agent's role is presentation. It doesn't use any tools to find new information. Instead, it takes the raw data gathered by the Researcher agent (passed via the State) and uses the LLM's language skills to transform it into a friendly, conversational response.

Add the following code to the bottom of agent.py:


# 1. Researcher Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that can access both internal zoo data and external knowledge from Wikipedia.",
    instruction="""
    You are a helpful research assistant. Your goal is to fully answer the user's PROMPT.
    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations).
    2. A tool for searching Wikipedia for general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND Wikipedia,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT:
    {{ PROMPT }}
    """,
    tools=[
        mcp_tools,
        wikipedia_tool
    ],
    output_key="research_data" # A key to store the combined findings
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - First, present the specific information from the zoo (like names, ages, and where to find them).
    - Then, add the interesting general facts from the research.
    - If some information is missing, just present the information you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    {{ research_data }}
    """
)
Step 4: The Workflow Agent
The workflow agent acts as the ‘back-office' manager for the zoo tour. It takes the research request and ensures the two agents we defined above perform their jobs in the correct order: first research, then formatting. This creates a predictable and reliable process for answering a visitor's question.

How: It's a SequentialAgent, a special type of agent that doesn't think for itself. Its only job is to run a list of sub_agents (the researcher and formatter) in a fixed sequence, automatically passing the shared memory from one to the next.

Add this block of code to the bottom of agent.py:


tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main workflow for handling a user's request about an animal.",
    sub_agents=[
        comprehensive_researcher, # Step 1: Gather all data
        response_formatter,       # Step 2: Format the final response
    ]
)
Final Step: Assemble the Main Workflow 1000b9d20f4e134b.jpeg
This Agent is designated as the root_agent, which the ADK framework uses as the starting point for all new conversations. Its primary role is to orchestrate the overall process. It acts as the initial controller, managing the first turn of the conversation.

Add this final block of code to the bottom of agent.py:


root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)
Your agent.py file is now complete! By building it this way, you can see how each component—tools, worker agents, and manager agents—has a specific role in creating the final, intelligent system. Next up, deployment!

Back
Next
bug_report Report a mistake
Skip to main content
Build and deploy an ADK agent that uses an MCP server on Cloud Run
access_time
32 mins remaining

English
Introduction
Why deploy to Cloud Run?
Setup and Requirements
Before you begin
Create the project folder
Create Agent Workflow
Prepare the application for deployment
Deploy the agent using the ADK CLI
Test the deployed agent
Clean up environment
Congratulations
Survey
7. Prepare the application for deployment
With your local environment ready, the next step is to prepare your Google Cloud project for the deployment. This involves a final check of your agent's file structure to ensure it's compatible with the deployment command. More importantly, you configure a critical IAM permission that allows your deployed Cloud Run service to act on your behalf and call the Vertex AI models. Completing this step ensures the cloud environment is ready to run your agent successfully.

Load the variables into your shell session by running the source command.


source .env
Grant the service account the Vertex AI User role, which gives it permission to make predictions and call Google's models.


# Grant the "Vertex AI User" role to your service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
Back
Next
bug_report Report a mistake
Skip to main content
Build and deploy an ADK agent that uses an MCP server on Cloud Run
access_time
67 mins remaining

English
Introduction
Why deploy to Cloud Run?
Setup and Requirements
Before you begin
Create the project folder
Create Agent Workflow
Prepare the application for deployment
Deploy the agent using the ADK CLI
Test the deployed agent
Clean up environment
Congratulations
Survey
5. Create the project folder
Create the project directory.
This command creates a main folder for the lab for the agent's source code.


cd && mkdir zoo_guide_agent && cd zoo_guide_agent
Create the requirements.txt file. This file lists the Python libraries your agent needs. The following command creates the file and populates it.


cloudshell edit requirements.txt

google-adk==1.14.0
langchain-community
wikipedia
Set variables for your current project, region, and user. This is a more robust way to run these commands.


export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
Create and open a .env file to authenticate the agent in the zoo_guide_agent directory.


cloudshell edit .env
The cloudshell edit command will open the .env file in the editor above the terminal. Enter the following in the .env file and head back to the terminal.


MODEL="gemini-2.5-flash"
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
Adding the MCP server URL. If you have completed lab 1, follow these steps to use the MCP server you created in lab 1:

Note: Run the following three commands if you have completed lab 1, and would like to use the MCP server created in that lab. You do not need to run these two commands if you already are using the public MCP server link provided to you during a live event.

Give the Cloud Run service identity permission to call the remote MCP server

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.invoker"
Save the MCP server URL from Lab 1 to an environment variable.

echo -e "\nMCP_SERVER_URL=https://zoo-mcp-server-${PROJECT_NUMBER}.europe-west1.run.app/mcp" >> .env
If you are using a public MCP server link, run the following, and replace PROJECT_NUMBER with what is provided.


echo -e "\nMCP_SERVER_URL=https://zoo-mcp-server-${PROJECT_NUMBER}.europe-west1.run.app/mcp" >> .env
Back
Next
bug_report Report a mistake
Skip to main content
Getting Started with MCP, ADK and A2A

Language
Overview
Before you begin
Installation
Create a local MCP Server
Deploy your MCP Server to Cloud Run
Create an Agent with Agent Development Kit (ADK)
Agent2Agent (A2A) Protocol
Exposing the Currency Agent A2A Server
Congratulations
4. Create a local MCP Server
Before you get to orchestrating your currency agent, you will first create an MCP server for exposing your tool(s) that your agent will need.

An MCP server let's you write lightweight programs to expose specific capabilities (like fetching currency exchange rates) as tools. An agent or even multiple agents can then access these tools using the standardized Model Context Protocol (MCP).

The FastMCP Python package can be leveraged to create an MCP server that exposes a single tool called get_exchange_rate. The get_exchange_rate tool makes a call over the internet to the Frankfurter API to get the current exchange rate between two currencies.

The code for the MCP server can be found in the mcp-server/server.py file:

import logging
import os

import httpx
from fastmcp import FastMCP

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Currency MCP Server 💵")

@mcp.tool()
def get_exchange_rate(
    currency_from: str = 'USD',
    currency_to: str = 'EUR',
    currency_date: str = 'latest',
):
    """Use this to get current exchange rate.

    Args:
        currency_from: The currency to convert from (e.g., "USD").
        currency_to: The currency to convert to (e.g., "EUR").
        currency_date: The date for the exchange rate or "latest". Defaults to "latest".

    Returns:
        A dictionary containing the exchange rate data, or an error message if the request fails.
    """
    logger.info(f"--- 🛠️ Tool: get_exchange_rate called for converting {currency_from} to {currency_to} ---")
    try:
        response = httpx.get(
            f'https://api.frankfurter.app/{currency_date}',
            params={'from': currency_from, 'to': currency_to},
        )
        response.raise_for_status()

        data = response.json()
        if 'rates' not in data:
            return {'error': 'Invalid API response format.'}
        logger.info(f'✅ API response: {data}')
        return data
    except httpx.HTTPError as e:
        return {'error': f'API request failed: {e}'}
    except ValueError:
        return {'error': 'Invalid JSON response from API.'}

if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=os.getenv("PORT", 8080),
        )
    )

To start the MCP server locally, open a terminal and run the following command (server will start on http://localhost:8080):

uv run mcp-server/server.py
Test that the MCP server is functioning properly and that the get_exchange_rate tool is accessible using the Model Context Protocol.

In a new terminal window (so that you don't stop the local MCP server) run the following:

uv run mcp-server/test_server.py
You should see the current exchange rate of 1 USD (US dollar) to EUR (Euro) outputted:

--- 🛠️ Tool found: get_exchange_rate ---
--- 🪛 Calling get_exchange_rate tool for USD to EUR ---
--- ✅ Success: {
  "amount": 1.0,
  "base": "USD",
  "date": "2025-05-26",
  "rates": {
    "EUR": 0.87866
  }
} ---
Awesome! You successfully have a working MCP server with a tool that your agent will be able to access.

Before moving on to the next station, stop the locally running MCP server by running Ctrl+C (or Command+C on Mac) in the terminal where you started it.

Back
Next
bug_report Report a mistake
Skip to main content
Getting Started with MCP, ADK and A2A

English
Overview
Before you begin
Installation
Create a local MCP Server
Deploy your MCP Server to Cloud Run
Create an Agent with Agent Development Kit (ADK)
Agent2Agent (A2A) Protocol
Exposing the Currency Agent A2A Server
Congratulations
5. Deploy your MCP Server to Cloud Run
Now you are ready to deploy the MCP server as a remote MCP server to Cloud Run 🚀☁️

Benefits of running an MCP server remotely
Running an MCP server remotely on Cloud Run can provide several benefits:

📈Scalability: Cloud Run is built to rapidly scale out to handle all incoming requests. Cloud Run will scale your MCP server automatically based on demand.
👥Centralized server: You can share access to a centralized MCP server with team members through IAM privileges, allowing them to connect to it from their local machines instead of all running their own servers locally. If a change is made to the MCP server, all team members will benefit from it.
🔐Security: Cloud Run provides an easy way to force authenticated requests. This allows only secure connections to your MCP server, preventing unauthorized access.
IMPORTANT: The security aspect previously mentioned is critical. If you don't enforce authentication, anyone on the public internet can potentially access and call your MCP server.

Change into the mcp-server directory:


cd mcp-server
Deploy the MCP server to Cloud Run:


gcloud run deploy mcp-server --no-allow-unauthenticated --region=us-central1 --source .
If your service has successfully deployed you will see a message like the following:


Service [mcp-server] revision [mcp-server-12345-abc] has been deployed and is serving 100 percent of traffic.
Authenticating MCP Clients
Since you specified --no-allow-unauthenticated to require authentication, any MCP client connecting to the remote MCP server will need to authenticate.

The official docs for Host MCP servers on Cloud Run provides more information on this topic depending on where you are running your MCP client.

You will need to run the Cloud Run proxy to create an authenticated tunnel to the remote MCP server on your local machine.

By default, the URL of Cloud Run services requires all requests to be authorized with the Cloud Run Invoker (roles/run.invoker) IAM role. This IAM policy binding ensures that a strong security mechanism is used to authenticate your local MCP client.

You should make sure that you or any team members trying to access the remote MCP server have the roles/run.invoker IAM role bound to their IAM principal (Google Cloud account).

NOTE: The following command may prompt you to download the Cloud Run proxy if it is not already installed. Follow the prompts to download and install it.

gcloud run services proxy mcp-server --region=us-central1
You should see the following output:

Proxying to Cloud Run service [mcp-server] in project [<YOUR_PROJECT_ID>] region [us-central1]
http://127.0.0.1:8080 proxies to https://mcp-server-abcdefgh-uc.a.run.app
All traffic to http://127.0.0.1:8080 will now be authenticated and forwarded to the remote MCP server.

Test the remote MCP server
In a new terminal, head back to the root folder and re-run the mcp-server/test_server.py file to make sure the remote MCP server is working.

NOTE: Make sure you leave the Cloud Run proxy running for the rest of the codelab.

cd ..
uv run mcp-server/test_server.py
You should see a similar output as you did when running the server locally:

--- 🛠️ Tool found: get_exchange_rate ---
--- 🪛 Calling get_exchange_rate tool for USD to EUR ---
--- ✅ Success: {
  "amount": 1.0,
  "base": "USD",
  "date": "2025-05-26",
  "rates": {
    "EUR": 0.87866
  }
} ---
You can query the logs of the deployed Cloud Run MCP server if you would like to verify that the remote server was indeed called:

gcloud run services logs read mcp-server --region us-central1 --limit 5
You should see the following outputted in the logs:

2025-06-04 14:28:29,871 [INFO]: --- 🛠️ Tool: get_exchange_rate called for converting USD to EUR ---
2025-06-04 14:28:30,610 [INFO]: HTTP Request: GET https://api.frankfurter.app/latest?from=USD&to=EUR "HTTP/1.1 200 OK"
2025-06-04 14:28:30,611 [INFO]: ✅ API response: {'amount': 1.0, 'base': 'USD', 'date': '2025-06-03', 'rates': {'EUR': 0.87827}}
Now that you have a remote MCP server, you can move on to creating an agent! 🤖

Back
Next
bug_report Report a mistake
Skip to main content
Getting Started with MCP, ADK and A2A

English
Overview
Before you begin
Installation
Create a local MCP Server
Deploy your MCP Server to Cloud Run
Create an Agent with Agent Development Kit (ADK)
Agent2Agent (A2A) Protocol
Exposing the Currency Agent A2A Server
Congratulations
6. Create an Agent with Agent Development Kit (ADK)
You have a deployed MCP server, now it is time to create the currency agent using Agent Development Kit (ADK).

Agent Development Kit recently released its v1.0.0 stable release. This milestone signifies that the Python ADK is now production-ready, offering a reliable and robust platform for developers to confidently build and deploy their agents in live environments.

ADK makes creating agents extremely lightweight and allows them to easily connect to MCP servers with built-in support for MCP Tools. The currency agent will access the get_exchange_rate tool by using ADK's MCPToolset class.

The code for the currency agent is located in currency_agent/agent.py:


import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a specialized assistant for currency conversions. "
    "Your sole purpose is to use the 'get_exchange_rate' tool to answer questions about currency exchange rates. "
    "If the user asks about anything other than currency conversion or exchange rates, "
    "politely state that you cannot help with that topic and can only assist with currency-related queries. "
    "Do not attempt to answer unrelated questions or use tools for other purposes."
)

logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
logger.info("--- 🤖 Creating ADK Currency Agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="currency_agent",
    description="An agent that can help with currency conversions",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
            )
        )
    ],
)
To quickly test out the currency agent you can take advantage of ADK's dev UI, accessed by running adk web:

uv run adk web
In a browser, head over to http://localhost:8000 to see and test the agent!

Make sure that currency_agent is selected as the agent in the top left corner of the web UI.

ADK Web UI

Ask your agent in the chat area something like "What is 250 CAD to USD?". You should see the agent call our get_exchange_rate MCP tool before it gives a response.

ADK Web Currency Agent

The agent works! It can handle queries that revolve around currency conversions 💸.

Back
Next
bug_report Report a mistake
Skip to main content
Getting Started with MCP, ADK and A2A

English
Overview
Before you begin
Installation
Create a local MCP Server
Deploy your MCP Server to Cloud Run
Create an Agent with Agent Development Kit (ADK)
Agent2Agent (A2A) Protocol
Exposing the Currency Agent A2A Server
Congratulations
7. Agent2Agent (A2A) Protocol
The Agent2Agent (A2A) Protocol is an open standard designed to enable seamless communication and collaboration between AI agents. This allows agents that are built using diverse frameworks and by different vendors, to communicate with one another in a common language, breaking down silos and fostering interoperability.

A2A Protocol

A2A allows agents to:

Discover: Find other agents and learn their skills (AgentSkill) and capabilities (AgentCapabilities) using standardized Agent Cards.
Communicate: Exchange messages and data securely.
Collaborate: Delegate tasks and coordinate actions to achieve complex goals.
The A2A protocol facilitates this communication through mechanisms like "Agent Cards" that act as digital business cards agents can use to advertise their capabilities and connection information.

A2A Agent Card

Now it is time to expose the currency agent using A2A so that it can be called by other agents and clients.

A2A Python SDK
The A2A Python SDK provides Pydantic models for each of the aforementioned resources; AgentSkill, AgentCapabilities and AgentCard. This provides an interface for expediting development and integration with the A2A protocol.

An AgentSkill is how you will advertise to other agents that the currency agent has a tool for get_exchange_rate:


# A2A Agent Skill definition
skill = AgentSkill(
    id='get_exchange_rate',
    name='Currency Exchange Rates Tool',
    description='Helps with exchange values between various currencies',
    tags=['currency conversion', 'currency exchange'],
    examples=['What is exchange rate between USD and GBP?'],
)
Then as part of the AgentCard it will list the agent's skills and capabilities alongside additional details like input and output modes that the agent can handle:


# A2A Agent Card definition
agent_card = AgentCard(
    name='Currency Agent',
    description='Helps with exchange rates for currencies',
    url=f'http://{host}:{port}/',
    version='1.0.0',
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[skill],
)
The time has come to put it all together with the currency agent and showcase the power of A2A!

Back
Next
bug_report Report a mistake
Skip to main content
Getting Started with MCP, ADK and A2A

English
Overview
Before you begin
Installation
Create a local MCP Server
Deploy your MCP Server to Cloud Run
Create an Agent with Agent Development Kit (ADK)
Agent2Agent (A2A) Protocol
Exposing the Currency Agent A2A Server
Congratulations
8. Exposing the Currency Agent A2A Server
ADK simplifies the process of building and connecting agents using the A2A protocol for you. Making an an existing ADK agent accessible (exposing) as an A2A server is done with ADK's to_a2a(root_agent) function (See the ADK documentation for the full details).

The to_a2a function converts an existing agent to work with A2A, and be able to expose it as a server through uvicorn. This means that you have tighter control over what you want to expose if you plan to productionize your agent. The to_a2a() function auto-generates an agent card based on your agent code using the A2A Python SDK under the hood.

Taking a look inside the file currency_agent/agent.py you can see the use of to_a2a and how the currency agent is exposed as an A2A server with only two lines of code!


from google.adk.a2a.utils.agent_to_a2a import to_a2a
# ... see file for full code

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10000)
To run the A2A server, in a new terminal run the following:


uv run uvicorn currency_agent.agent:a2a_app --host localhost --port 10000
If the server starts successfully, the output will look as follows indicating it is running on port 10000:


[INFO]: --- 🔧 Loading MCP tools from MCP Server... ---
[INFO]: --- 🤖 Creating ADK Currency Agent... ---
INFO:     Started server process [45824]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:10000 (Press CTRL+C to quit)
The currency agent is now successfully running as an A2A server, with the ability to be called by other agents or clients using the A2A protocol!

Verify the Remote Agent is Running
You can double-check that your agent is up and running by visiting the agent card URL for the currency agent that was auto-generated by the to_a2a() function.

In your browser, head to [http://localhost:10000/.well-known/agent.json]

You should see the following agent card:

{
  "capabilities": {

  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "description": "An agent that can help with currency conversions",
  "name": "currency_agent",
  "preferredTransport": "JSONRPC",
  "protocolVersion": "0.3.0",
  "skills": [
    {
      "description": "An agent that can help with currency conversions I am a specialized assistant for currency conversions. my sole purpose is to use the 'get_exchange_rate' tool to answer questions about currency exchange rates. If the user asks about anything other than currency conversion or exchange rates, politely state that I cannot help with that topic and can only assist with currency-related queries. Do not attempt to answer unrelated questions or use tools for other purposes.",
      "id": "currency_agent",
      "name": "model",
      "tags": [
        "llm"
      ]
    },
    {
      "description": "Use this to get current exchange rate.\n\nArgs:\n    currency_from: The currency to convert from (e.g., \"USD\").\n    currency_to: The currency to convert to (e.g., \"EUR\").\n    currency_date: The date for the exchange rate or \"latest\". Defaults to \"latest\".\n\nReturns:\n    A dictionary containing the exchange rate data, or an error message if the request fails.",
      "id": "currency_agent-get_exchange_rate",
      "name": "get_exchange_rate",
      "tags": [
        "llm",
        "tools"
      ]
    }
  ],
  "supportsAuthenticatedExtendedCard": false,
  "url": "http://localhost:10000",
  "version": "0.0.1"
}
Test the A2A Server
You can now test the server by sending it some requests using A2A!

The A2A Python SDK provides an a2a.client.A2AClient class that simplifies this for you.

Note: If you had a multi-agent architecture you would use a similar pattern to what you have done here with the A2AClient.

The file currency_agent/test_client.py contains code that runs through several different test cases against the A2A server.

# ... see file for full code

# Example test using A2AClient
async def run_single_turn_test(client: A2AClient) -> None:
    """Runs a single-turn non-streaming test."""

    send_message_payload = create_send_message_payload(text="how much is 100 USD in CAD?")
    request = SendMessageRequest(
        id=str(uuid4()), params=MessageSendParams(**send_message_payload)
    )

    print("--- ✉️  Single Turn Request ---")
    # Send Message
    response: SendMessageResponse = await client.send_message(request)
    print_json_response(response, "📥 Single Turn Request Response")
    if not isinstance(response.root, SendMessageSuccessResponse):
        print("received non-success response. Aborting get task ")
        return

    if not isinstance(response.root.result, Task):
        print("received non-task response. Aborting get task ")
        return

    task_id: str = response.root.result.id
    print("--- ❔ Query Task ---")
    # query the task
    get_request = GetTaskRequest(id=str(uuid4()), params=TaskQueryParams(id=task_id))
    get_response: GetTaskResponse = await client.get_task(get_request)
    print_json_response(get_response, "📥 Query Task Response")

# ----- Main Entrypoint (Create client --> Run tests) -----
async def main() -> None:
    """Main function to run the tests."""
    print(f'--- 🔄 Connecting to agent at {AGENT_URL}... ---')
    try:
        async with httpx.AsyncClient() as httpx_client:
            # Create a resolver to fetch the agent card
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=AGENT_URL,
            )
            agent_card = await resolver.get_agent_card()
            # Create a client to interact with the agent
            client = A2AClient(
                httpx_client=httpx_client,
                agent_card=agent_card,
            )
            print('--- ✅ Connection successful. ---')

            await run_single_turn_test(client)
            await run_multi_turn_test(client)

    except Exception as e:
        traceback.print_exc()
        print(f'--- ❌ An error occurred: {e} ---')
        print('Ensure the agent server is running.')
Run the tests using the following command:

uv run currency_agent/test_client.py
A successful test run will result in the following:

--- 🔄 Connecting to agent at http://localhost:10000... ---
--- ✅ Connection successful. ---
--- ✉️ Single Turn Request ---
--- 📥 Single Turn Request Response ---
{"id":"3bc92d7b-d857-4e93-9ff0-b2fb865f6e35","jsonrpc":"2.0","result":{"artifacts":[{"artifactId":"35e89e14-b977-4397-a23b-92c84bc32379","parts":[{"kind":"text","text":"Based on the current exchange rate, 1 USD is equivalent to 1.3704 CAD. Therefore, 100 USD would be 137.04 CAD.\n"}]}],"contextId":"2d66f277-152c-46ef-881d-7fe32866e9f5","history":[{"contextId":"2d66f277-152c-46ef-881d-7fe32866e9f5","kind":"message","messageId":"59819269f7d04849b0bfca7d43ec073c","parts":[{"kind":"text","text":"how much is 100 USD in CAD?"}],"role":"user","taskId":"52ae2392-84f5-429a-a14b-8413d3d20d97"},{"contextId":"2d66f277-152c-46ef-881d-7fe32866e9f5","kind":"message","messageId":"286095c6-12c9-40cb-9596-a9676d570dbd","parts":[],"role":"agent","taskId":"52ae2392-84f5-429a-a14b-8413d3d20d97"}],"id":"52ae2392-84f5-429a-a14b-8413d3d20d97","kind":"task","status":{"state":"completed"}}}

// ...

--- 🚀 First turn completed, no further input required for this test case. ---
It works! You have successfully tested that you can communicate with the currency agent over an A2A server! 🎉

Check out the a2a-samples repository on GitHub to see more advanced use-cases!

Looking to deploy your agent? Vertex AI Agent Engine provides a managed experience for deploying AI agents to production!

Back
Next
bug_report Report a mistake
Skip to main content
Create multi agent system with ADK, deploy in Agent Engine and get started with A2A protocol

English
Objective of this lab
Before you begin
Overview: Benefits of Agent Development Kit
Introduction to A2A
Agent Architecture
Task 1. Install ADK and set up your environment
Task 2. Deploy to Agent Engine
Task 3. Create an A2A agent
Clean up
4. Introduction to A2A
The Agent2Agent (A2A) protocol is an open standard designed to enable seamless and secure communication and collaboration between autonomous AI agents from different frameworks, vendors, and domains.

Universal Interoperability: A2A allows agents to work together regardless of their underlying technologies, fostering a truly multi-agent ecosystem. This means agents built by different companies on different platforms can communicate and coordinate.
Capability Discovery: Agents can advertise their capabilities using "Agent Cards" (JSON documents), which describe their identity, supported A2A features, skills, and authentication requirements. This allows other agents to discover and select the most suitable agent for a given task.
Secure by Default: Security is a core principle. A2A incorporates enterprise-grade authentication and authorization mechanisms, utilizing standards like HTTPS/TLS, JWT, OIDC, and API keys to ensure secure interactions and protect sensitive data.
Modality Agnostic: The protocol supports various communication modalities, including text, audio, and video streaming, as well as interactive forms and embedded iframes. This flexibility allows agents to exchange information in the most appropriate format for the task and user.
Structured Task Management: A2A defines clear protocols for task delegation, monitoring, and completion. It supports grouping related tasks and managing them across different agents using unique task IDs. Tasks can transition through defined lifecycles (e.g., submitted, working, completed).
Opaque Execution: A significant feature is that agents don't need to reveal their internal reasoning processes, memory, or specific tools to other agents. They only expose their callable services, promoting modularity and privacy.
Built on Existing Standards: A2A leverages established web technologies such as HTTP, Server-Sent Events (SSE) for real-time streaming, and JSON-RPC for structured data exchange, making it easier to integrate with existing IT infrastructure.
Asynchronous Communication: The protocol is designed with asynchronous communication as a primary consideration, facilitating flexible task progression and enabling push notifications for updates even when a connection isn't persistently maintained.
Back
Next
bug_report Report a mistake
Skip to main content
Create multi agent system with ADK, deploy in Agent Engine and get started with A2A protocol

English
Objective of this lab
Before you begin
Overview: Benefits of Agent Development Kit
Introduction to A2A
Agent Architecture
Task 1. Install ADK and set up your environment
Task 2. Deploy to Agent Engine
Task 3. Create an A2A agent
Clean up
5. Agent Architecture
In this lab, you will create a multi-agent application that generates an image according to your specification and evaluates the image before presenting it to you.

The system is structured with a main agent called image_scoring that orchestrates the entire process. This main agent has a sub-agent called image_generation_scoring_agent which in turn has its own sub-agents for more specific tasks. This creates a hierarchical relationship where the main agent delegates tasks to its sub-agents. 6e21de5b4f92669c.png Figure 2: Overall Agent flow.

List of All Agents

image_scoring (Main Agent):
Purpose: This is the root agent that manages the overall workflow. It repeatedly runs the image_generation_scoring_agent and the checker_agent in a loop until a termination condition is met.
Sub-agents:
image_generation_scoring_agent
checker_agent_instance
image_generation_scoring_agent (Sub-agent of image_scoring):
Purpose: This agent is responsible for the core logic of generating and scoring images. It executes a sequence of three sub-agents to achieve this.
Sub-agents:
image_generation_prompt_agent
image_generation_agent
scoring_images_prompt
checker_agent_instance (Sub-agent of image_scoring):
Purpose: This agent checks if the image scoring process should continue or terminate. It uses the check_tool_condition tool to evaluate the termination condition.
image_generation_prompt_agent (Sub-agent of image_generation_scoring_agent):
Purpose: This agent is an expert in creating prompts for image generation. It takes an input text and generates a detailed prompt suitable for the image generation model.
image_generation_agent (Sub-agent of image_generation_scoring_agent):
Purpose: This agent is an expert in creating images using Imagen 3. It takes the prompt from the image_generation_prompt_agent and generates an image.
scoring_images_prompt (Sub-agent of image_generation_scoring_agent):
Purpose: This agent is an expert in evaluating and scoring images based on various criteria. It takes the generated image and assigns a score to it.
Tools Used by the Agents

check_tool_condition:
Description: This tool checks if the loop termination condition is met or if the maximum number of iterations has been reached. If either of these is true, it stops the loop.
Used by: checker_agent_instance
generate_images:
Description: This tool generates images using the Imagen 3 model. It can also save the generated images to a Google Cloud Storage bucket.
Used by: image_generation_agent
get_policy:
Description: This tool fetches a policy from a JSON file. The policy is used by the image_generation_prompt_agent to create the image generation prompt and by the scoring_images_prompt to score the images.
Used by: image_generation_prompt_agent, scoring_images_prompt
get_image:
Description: This tool loads the generated image artifact so that it can be scored.
Used by: scoring_images_prompt
set_score:
Description: This tool sets the total score of the generated image in the session state.
Used by: scoring_images_prompt
Back
Next
bug_report Report a mistake
Skip to main content
Create multi agent system with ADK, deploy in Agent Engine and get started with A2A protocol

English
Objective of this lab
Before you begin
Overview: Benefits of Agent Development Kit
Introduction to A2A
Agent Architecture
Task 1. Install ADK and set up your environment
Task 2. Deploy to Agent Engine
Task 3. Create an A2A agent
Clean up
6. Task 1. Install ADK and set up your environment
In this Hands on we will use Cloud Shell to perform the tasks.

Enable Vertex AI recommended APIs
In the Google Cloud console, navigate to Vertex AI by searching for it at the top of the console.
Click Enable all recommended APIs.
Prepare a Cloud Shell Editor tab
With your Google Cloud console window selected, open Cloud Shell by pressing the G key and then the S key on your keyboard. Alternatively, you can click the cloud shell button 231dc0e6754519c8.pngon the top right corner of the Google Cloud Console.
Click Continue.
When prompted to authorize Cloud Shell, click Authorize.
In the upper right corner of the Cloud Shell pane, click the Open in new window button Open in new window button.
Click the Open Editor pencil icon ( Open Editor pencil icon) at the top of the pane to view files.
At the top of the left-hand navigation menu, click the Explorer icon Explorer icon to open your file explorer.
Click the Open Folder button.
Throughout the rest of this lab, you can work in this window as your IDE with the Cloud Shell Editor and Cloud Shell Terminal.
Download and install the ADK and code samples for this lab
Execute the following commands to clone the needed source from github and install necessary libraries.

#create the project directory
mkdir imagescoring
cd imagescoring
#clone the code in the local directory
git clone https://github.com/haren-bh/multiagenthandson.git

#Create the virtual environment
python3 -m venv pythonenv
source pythonenv/bin/activate

#install google-adk and a2a sdk
python3 -m pip install google-adk==1.8.0
python3 -m pip install a2a-sdk==0.2.16
We will use poetry to install additional requirements:

cd multiagenthandson #go to the application directory
pip install poetry poetry-plugin-export
poetry install --with deployment
If you do not have a cloud storage bucket, create a new one in Google Cloud Storage. You can also create the bucket using gsutil command.

gsutil mb gs://YOUR-UNIQUE-BUCKETNAME
In the editor go to View->Toggle hidden files. And in the image_scoring folder create a .env file with the following content. Add the required details such as your project name and cloud storage bucket.

GOOGLE_GENAI_USE_VERTEXAI=1 #1 if VERTEXAI has to be used. Can be 0 if API_KEY is specified
GOOGLE_CLOUD_PROJECT=YOUR CLOUD PROJECT NAME
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=YOUR BUCKET NAME  # Only required for deployment on Agent Engine
GCS_BUCKET_NAME=YOUR BUCKET NAME #Bucket for storing generated images.
SCORE_THRESHOLD=40 # Min threshold for image_score. Max Score is 50 , hence should be less than 50. 
#If the computed score is higher then loop will terminate
#MAX_ITERATIONS=5 #Max iterations for evaluating the image_score before terminating the loop.
IMAGEN_MODEL="imagen-3.0-generate-002" 
GENAI_MODEL="gemini-2.5-flash"
#AGENT_ENGINE_ID=<AGENT_ENGINE_ID> #The Agent Engine ID obtained after deploying to the agent engine.
Look at the agent structure in the source code, start at agent.py . This agent contains the root agent that will connect to the other agents.
Go back to the top directory multiagenthandson in the terminal and execute the following command to run the agent locally

# Run the following command to run agents locally
export GCS_BUCKET_NAME=your gcs bucket name
adk web
7bb4bc5f8244c140.png Figure 1

Ctrl+Click (CMD+Click for MacOS) on the http:// url displayed on the terminal to open the ADK's browser based GUI client. It should look like Figure 2

Let's generate some images. Try the following prompts or your own prompts.
A peaceful mountain landscape at sunset
A cat riding a bicycle
99e23472f80a81f2.png Figure 2

Back
Next
bug_report Report a mistake
Skip to main content
Create multi agent system with ADK, deploy in Agent Engine and get started with A2A protocol

English
Objective of this lab
Before you begin
Overview: Benefits of Agent Development Kit
Introduction to A2A
Agent Architecture
Task 1. Install ADK and set up your environment
Task 2. Deploy to Agent Engine
Task 3. Create an A2A agent
Clean up
7. Task 2. Deploy to Agent Engine
Now we deploy the agent to the Agent Engine. Agent Engine is a fully managed service for deploying agents in GCP. Agent Engine is compatible with ADK so the agents built with ADK can be deployed in Agent Engine.

Define some environment variables

export GOOGLE_CLOUD_LOCATION='us-central1'
export GOOGLE_CLOUD_PROJECT='your project id'
Create the requirements.txt file using poetry. Poetry will use pyproject.toml to create requirements.txt file. After running the command check if requirements.txt file has been created.

# Go to the parent folder containing pyproject.toml file
# install poetry-plugin-export
pip install poetry-plugin-export

#Create requirements.txt file
poetry export -f requirements.txt --output requirements.txt --without-hashes
Create the package. We need to bundle our app into a .whl python package. We will use poetry to do that. Once you execute the command make sure a dist folder is created and it contains the .whl file.

# Go to the parent folder containing pyproject.toml file
#Create python package, to create whl file
poetry build
Now we will prepare the deploy script. The deploy script will deploy our image-scoring agent or agent engine service. Please change the content of deploy.py inside the image_scoring folder as below.

# Change the content of the following. Look for #change this comment
import vertexai
from .agent import root_agent
import os
import glob # To easily find the wheel file

PROJECT_ID = "YOUR PROJECT ID" #change this your project
LOCATION = "us-central1" #change this
STAGING_BUCKET = "gs://YOUR BUCKET " #change this to your bucket

from vertexai import agent_engines

vertexai.init(
   project=PROJECT_ID,
   location=LOCATION,
   staging_bucket=STAGING_BUCKET,
)

remote_app = agent_engines.create(
   agent_engine=root_agent,
   requirements=open(os.path.join(os.getcwd(), "requirements.txt")).readlines()+["./dist/image_scoring-0.1.0-py3-none-any.whl"],#change this to your local location
   extra_packages=[
       "./dist/image_scoring-0.1.0-py3-none-any.whl", # change this to your location
   ]
)

print(remote_app.resource_name)
We can now run the deploy script.
#run deploy script from the parent folder containing deploy.py
python3 -m image_scoring.deploy
After you deploy you should see something like below, 13109f2a5c5c5af9.png

Figure 3

Now let's test the deployed agent. In order to test the remotely deployed agent engine first copy the agent location from the deploy output in the terminal. It should look something like this, projects/85469421903/locations/us-central1/reasoningEngines/7369674597261639680 .
Go to the folder testclient, open the file remote_test.py and edit the following lines.
PROJECT_ID = "" #change this
LOCATION = "" #change this
STAGING_BUCKET = "" #change this

#replace the id with your own.
reasoning_engine_id="your agent engine id"

#You can replace this with your own prompt
image_prompt="A cat riding a bicycle"

#execute remote_test.py
python3 remote_test.py
Back
Next
bug_report Report a mistake
Skip to main content
Create multi agent system with ADK, deploy in Agent Engine and get started with A2A protocol

English
Objective of this lab
Before you begin
Overview: Benefits of Agent Development Kit
Introduction to A2A
Agent Architecture
Task 1. Install ADK and set up your environment
Task 2. Deploy to Agent Engine
Task 3. Create an A2A agent
Clean up
8. Task 3. Create an A2A agent
In this step we are going to create a simple A2A agent based on the agent we created in the previous steps. Existing ADK agents can be published under A2A protocol. These are the key things you will learn in this step.

Learn the basics of A2A protocol.
Learn how ADK and A2A protocols work with each other.
Learn how to interact with A2A protocol.
In this hands on we will use the code in image_scoring_adk_a2a_server folder. Before you start the task please change your directory to this folder.

Create A2A agent card
A2A protocol requires an agent card that contains all the information about the agent such as agent capabilities, agent usage guide etc. Once an A2A agent is deployed the agent card is viewable using the ".well-known/agent-card.json" link. Clients can refer to this information to send the request to agents.

In the remote_a2a/image_scoring folder confirm there is agents.json with the following content.


{
 "name": "image_scoring",
 "description": "Agent that generates images based on user prompts and scores their adherence to the prompt.",
 "url": "http://localhost:8001/a2a/image_scoring",
 "version": "1.0.0",
 "defaultInputModes": ["text/plain"],
 "defaultOutputModes": ["image/png", "text/plain"],
 "capabilities": {
   "streaming": true,
   "functions": true
 },
 "skills": [
   {
     "id": "generate_and_score_image",
     "name": "Generate and Score Image",
     "description": "Generates an image from a given text prompt and then evaluates how well the generated image adheres to the original prompt, providing a score.",
     "tags": ["image generation", "image scoring", "evaluation", "AI art"],
     "examples": [
       "Generate an image of a futuristic city at sunset",
       "Create an image of a cat playing a piano",
       "Show me an image of a serene forest with a hidden waterfall"
     ]
   }
 ]
}
Create A2A agent

Within the root folder image_scoring_adk_a2a_server, confirm that there is an a2a_agent.py file, which is the entry point for a2a agent. It should have following content,


from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

root_agent = RemoteA2aAgent(
   name="image_scoring",
   description="Agent to give interesting facts.",
   agent_card="http://localhost:8001/a2a/image_scoring/.well-known/agent.json",
  
   # Optional configurations
   timeout=300.0,          # HTTP timeout (seconds)
   httpx_client=None,      # Custom HTTP client
)
Run A2A agent

Now we are ready to run the agent! To run the agent execute following command from inside the top folder image_scoring_adk_a2a_server


#set some environmental variables
export GOOGLE_CLOUD_PROJECT=datapipeline-372305
export GOOGLE_CLOUD_LOCATION=us-central1
export GCS_BUCKET_NAME=haren-genai-bucket

#following command runs the ADK agent as a2a agent
adk api_server --a2a --port 8001 remote_a2a
Test A2A agent
Once the agent is running we can now go and test the agent. First of all, let's go ahead and check the agent card.

#Execute the following 
curl http://localhost:8001/a2a/image_scoring/.well-known/agent.json
Executing the above should show the agent card for our A2A agent, which is mainly the content of agent.json that we created in the previous step.

Let's now send a request to the agent. We can use curl to send request to the agent,

curl -X POST   http://localhost:8001/a2a/image_scoring   -H 'Content-Type: application/json'   -d '{
    "id": "uuid-123",
    "params": {
      "message": {
        "messageId": "msg-456",
        "parts": [{"text": "Create an image of a cat"}],
        "role": "user"
      }
    }
  }'
In the above request, you can change the prompt by changing the "Create an image of a cat" line. Once you run the command, you can check for the output image in the specified google cloud storage.

Back
Next
bug_report Report a mistake
Skip to main content
Google's Agent Stack in Action: ADK, A2A, MCP on Google Cloud

English
What you will learn
Architecture
Before you begin
Setup Graph Database
Current state of InstaVibe
Basic Agent,Event Planner with ADK
Platform Interaction Agent - interact with MCP Server
Platform Interaction Agent (using MCP)
Workflow Agent and Multi-Agents in ADK
Agent-to-Agent (A2A) Communication
Orchestrator Agent (A2A Client)
Agent Engine and Remote Call from InstaVibe
Clean Up
Google's Agent Stack in Action:ADK, A2A, MCP on Google Cloud
About this codelab
subjectLast updated Aug 14, 2025
account_circleWritten by Christina Lin
1. What you will learn
Welcome! We're about to embark on a pretty cool journey today. Let's start by thinking about a popular social event platform InstaVibe. While it's successful, we know that for some users, the actual planning of group activities can feel like a chore. Imagine trying to figure out what all your friends are interested in, then sifting through endless options for events or venues, and finally coordinating everything. It's a lot! This is precisely where we can introduce AI, and more specifically, intelligent agents, to make a real difference.

The idea is to build a system where these agents can handle the heavy lifting, like cleverly ‘listening' to understand user and friend preferences, and then proactively suggesting fantastic, tailored activities. Our aim is to transform social planning on InstaVibe into something seamless and delightful. To get started on building these smart assistants, we need to lay a strong groundwork with the right tools.

Here's the concept you'll see:

Title Page 

Foundations with Google's ADK: Master the fundamentals of building your first intelligent agent using Google's Agent Development Kit (ADK). Understand the essential components, the agent lifecycle, and how to leverage the framework's built-in tools effectively.

Extending Agent Capabilities with Model Context Protocol (MCP): Learn to equip your agents with custom tools and context, enabling them to perform specialized tasks and access specific information. Introduce the Model Context Protocol (MCP) concept. You'll learn how to set up an MCP server to provide this context.

Designing Agent Interactions & Orchestration: Move beyond single agents to understand agent orchestration. Design interaction patterns ranging from simple sequential workflows to complex scenarios involving loops, conditional logic, and parallel processing. Introduce the concept of sub-agents within the ADK framework to manage modular tasks.

Building Collaborative Multi-Agent Systems: Discover how to architect systems where multiple agents collaborate to achieve complex goals. Learn and implement the Agent-to-Agent (A2A) communication protocol, establishing a standardized way for distributed agents (potentially running on different machines or services) to interact reliably.

Productionizing Agents on Google Cloud: Transition your agent applications from development environments to the cloud. Learn best practices for architecting and deploying scalable, robust multi-agent systems on Google Cloud Platform (GCP). Gain insights into leveraging GCP services like Cloud Run and explore the capabilities of the latest Google Agent Engine for hosting and managing your agents.

Back
Next
bug_report Report a mistake
