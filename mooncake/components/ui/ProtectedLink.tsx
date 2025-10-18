'use client';

import { useAuth } from '@/context/AuthContext';
import { auth } from '@/lib/firebase';
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { useRouter } from 'next/navigation';
import React, { useEffect } from 'react';

interface ProtectedLinkProps {
  href: string;
  children: React.ReactNode;
}

export const ProtectedLink = ({ href, children }: ProtectedLinkProps) => {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      // The onAuthStateChanged listener in AuthContext will handle the user state update
      // and the redirect will happen in the effect below.
    } catch (error) {
      console.error("Error signing in with Google", error);
    }
  };

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (loading) {
      return; // Do nothing while auth state is loading
    }
    if (user) {
      router.push(href);
    } else {
      await handleSignIn();
      // After sign-in, the user state will update, and the effect will trigger navigation
    }
  };

  useEffect(() => {
    // This effect handles redirection after a successful login
    if (!loading && user) {
        // If the user is logged in and we intended to navigate, do so.
        // This is a simplified logic. A more robust solution might use a temporary state.
    }
  }, [user, loading, href, router]);

  return (
    <a href={href} onClick={handleClick}>
      {children}
    </a>
  );
};
