/**
 * AdminUsers - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Users, RefreshCw, Search, Crown, Shield } from 'lucide-react';
import AdminService from '../AdminService';

const AdminUsers = () => {
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const result = await AdminService.getUsers(50);
    if (result.success) setUsers(result.users || []);
    setLoading(false);
  };

  const filteredUsers = users.filter(u => 
    (u.email || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (u.name || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const roleIcon = (role) => {
    switch(role) {
      case 'admin': return <Shield className="h-4 w-4 text-red-500" />;
      case 'guide': return <Crown className="h-4 w-4 text-[#F5A623]" />;
      default: return <Users className="h-4 w-4 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-users" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Users className="h-6 w-6 text-[#F5A623]" />
          Gestion Utilisateurs
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
        <Input
          placeholder="Rechercher un utilisateur..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 bg-[#0d0d1a] border-[#F5A623]/20 text-white"
        />
      </div>

      {/* Users List */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">
            {filteredUsers.length} utilisateur{filteredUsers.length > 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredUsers.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Aucun utilisateur trouvé</p>
          ) : (
            <div className="space-y-2">
              {filteredUsers.map((user, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    {roleIcon(user.role)}
                    <div>
                      <p className="text-white font-medium">{user.name || user.email}</p>
                      <p className="text-gray-500 text-sm">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Badge className={`
                      ${user.role === 'admin' ? 'bg-red-500/20 text-red-400' : ''}
                      ${user.role === 'guide' ? 'bg-[#F5A623]/20 text-[#F5A623]' : ''}
                      ${user.role === 'hunter' || !user.role ? 'bg-gray-500/20 text-gray-400' : ''}
                    `}>
                      {user.role || 'hunter'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminUsers;
