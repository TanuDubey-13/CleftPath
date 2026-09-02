import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass } from 'lucide-react';
import { EmptyState } from '../components/ui/EmptyState';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="py-12 sm:py-20 flex items-center justify-center">
      <EmptyState
        icon={<Compass className="w-8 h-8 text-teal-900" />}
        title="Page Not Found"
        description="The path you are looking for might have been moved or does not exist. Let's guide you back to the family care dashboard."
        actionLabel="Back to Dashboard"
        onAction={() => navigate('/dashboard')}
      />
    </div>
  );
};
