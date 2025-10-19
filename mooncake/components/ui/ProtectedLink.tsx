'use client';

import { useAuth } from '@/context/AuthContext';
import { auth } from '@/lib/firebase';
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { useRouter } from 'next/navigation';
import React from 'react';

interface ProtectedLinkProps {
  href: string;
  children: React.ReactNode;
}

export const ProtectedLink = ({ href, children }: ProtectedLinkProps) => {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleSignInAndRedirect = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      // After a successful sign-in, onAuthStateChanged will update the user context.
      // We can then navigate to the protected route.
      router.push(href);
    } catch (error) {
      // Don't log "popup-closed-by-user" as an error in the console
      if (error.code !== 'auth/popup-closed-by-user') {
        console.error("Error signing in with Google", error);
      }
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (loading) {
      return; // Do nothing while auth state is loading
    }
    if (user) {
      router.push(href);
    } else {
      handleSignInAndRedirect();
    }
  };

  return (
    <a href={href} onClick={handleClick}>
      {children}
    </a>
  );
};
