/**
 * UserProfile - User profile display component
 * Phase 9 - Business Modules
 */
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { User, Target, Star, Handshake, Wrench, Crown, MapPin } from 'lucide-react';
import { SpeciesIcon } from '../../../components/bionic/SpeciesIcon';

export const UserProfile = ({ user, profile = null, compact = false }) => {
  const ROLE_ICONS = {
    guest: User,
    user: Target,
    premium: Star,
    partner: Handshake,
    admin: Wrench,
    super_admin: Crown
  };

  if (!user) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4 text-center text-slate-400">
          <User className="h-8 w-8 mx-auto text-slate-500" />
          <p className="text-sm mt-2">Utilisateur non connecté</p>
        </CardContent>
      </Card>
    );
  }

  const getRoleColor = (role) => {
    const colors = {
      guest: 'slate',
      user: 'blue',
      premium: 'amber',
      partner: 'purple',
      admin: 'red',
      super_admin: 'rose'
    };
    return colors[role] || 'slate';
  };

  const getRoleIcon = (role) => {
    const IconComponent = ROLE_ICONS[role] || User;
    return <IconComponent className="h-5 w-5" />;
  };

  if (compact) {
    return (
      <div className="flex items-center gap-3 bg-slate-800/80 rounded-lg px-3 py-2">
        <span className="text-xl">{getRoleIcon(user.role)}</span>
        <div>
          <p className="text-white font-medium text-sm">{user.name}</p>
          <Badge className={`bg-${getRoleColor(user.role)}-900/50 text-${getRoleColor(user.role)}-400 text-xs`}>
            {user.role}
          </Badge>
        </div>
      </div>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            {getRoleIcon(user.role)}
            Profil Utilisateur
          </span>
          <Badge className={`bg-${getRoleColor(user.role)}-900/50 text-${getRoleColor(user.role)}-400`}>
            {user.role}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Basic Info */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Nom</span>
            <span className="text-white font-medium">{user.name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Email</span>
            <span className="text-white">{user.email}</span>
          </div>
          {user.created_at && (
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Membre depuis</span>
              <span className="text-slate-300">
                {new Date(user.created_at).toLocaleDateString('fr-CA')}
              </span>
            </div>
          )}
        </div>

        {/* Hunting Profile */}
        {profile && (
          <div className="mt-4 pt-4 border-t border-slate-700">
            <h4 className="text-white font-medium text-sm mb-3 flex items-center gap-2">
              <SpeciesIcon species="deer" size="sm" />
              Profil de Chasse
            </h4>
            <div className="grid grid-cols-2 gap-3">
              {profile.experience_years && (
                <div className="bg-slate-700/50 rounded-lg p-2 text-center">
                  <div className="text-lg font-bold text-emerald-400">
                    {profile.experience_years}
                  </div>
                  <div className="text-xs text-slate-400">Années exp.</div>
                </div>
              )}
              {profile.preferred_species && (
                <div className="bg-slate-700/50 rounded-lg p-2 text-center">
                  <Target className="h-5 w-5 text-[#f5a623] mx-auto" />
                  <div className="text-xs text-slate-300">
                    {profile.preferred_species.join(', ')}
                  </div>
                </div>
              )}
              {profile.total_hunts && (
                <div className="bg-slate-700/50 rounded-lg p-2 text-center">
                  <div className="text-lg font-bold text-blue-400">
                    {profile.total_hunts}
                  </div>
                  <div className="text-xs text-slate-400">Chasses</div>
                </div>
              )}
              {profile.region && (
                <div className="bg-slate-700/50 rounded-lg p-2 text-center">
                  <MapPin className="h-5 w-5 text-[#f5a623] mx-auto" />
                  <div className="text-xs text-slate-300">{profile.region}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UserProfile;
