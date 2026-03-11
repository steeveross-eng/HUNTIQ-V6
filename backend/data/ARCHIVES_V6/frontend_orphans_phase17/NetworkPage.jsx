/**
 * NetworkPage - Networking Ecosystem page wrapper
 * BIONIC™ Global Container Applied
 */

import React from 'react';
import NetworkingHub from '@/components/NetworkingHub';
import { GlobalContainer } from '@/core/layouts';

const NetworkPage = () => {
  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        <NetworkingHub />
      </GlobalContainer>
    </main>
  );
};

export default NetworkPage;
