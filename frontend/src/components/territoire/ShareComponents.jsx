/**
 * ShareWaypointDialog - Dialog de partage de waypoint
 */

import React, { useState, useCallback } from 'react';
import { 
  Share2, Link2, Mail, Users, Copy, Check, X, 
  Send, Plus, UserPlus, Globe, Lock, Lightbulb
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter 
} from '@/components/ui/dialog';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useWaypointSharing, useHuntingGroups } from '@/hooks/useSharing';
import { toast } from 'sonner';

export const ShareWaypointDialog = ({ 
  open, 
  onOpenChange, 
  waypoint, 
  userId,
  onShared 
}) => {
  const [activeTab, setActiveTab] = useState('email');
  const [emails, setEmails] = useState('');
  const [message, setMessage] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [linkCopied, setLinkCopied] = useState(false);
  const [generatedLink, setGeneratedLink] = useState(null);
  
  const { loading, shareByEmail, createShareLink } = useWaypointSharing(userId);
  const { allGroups, shareWaypointWithGroup, loading: groupsLoading } = useHuntingGroups(userId);

  const handleShareByEmail = useCallback(async () => {
    const emailList = emails
      .split(/[,;\n]/)
      .map(e => e.trim())
      .filter(e => e && e.includes('@'));
    
    if (emailList.length === 0) {
      toast.error('Entrez au moins une adresse email valide');
      return;
    }
    
    const result = await shareByEmail(
      waypoint.id, 
      waypoint.name, 
      emailList, 
      message || null
    );
    
    if (result) {
      setEmails('');
      setMessage('');
      if (onShared) onShared(result);
    }
  }, [emails, message, waypoint, shareByEmail, onShared]);

  const handleCreateLink = useCallback(async () => {
    const result = await createShareLink(waypoint.id, waypoint.name, 30);
    if (result) {
      setGeneratedLink(result.share_url);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 3000);
    }
  }, [waypoint, createShareLink]);

  const handleShareWithGroup = useCallback(async () => {
    if (!selectedGroupId) {
      toast.error('Sélectionnez un groupe');
      return;
    }
    
    const success = await shareWaypointWithGroup(
      selectedGroupId, 
      waypoint.id, 
      waypoint.name
    );
    
    if (success && onShared) {
      onShared({ type: 'group', groupId: selectedGroupId });
    }
  }, [selectedGroupId, waypoint, shareWaypointWithGroup, onShared]);

  const copyLink = useCallback(() => {
    if (generatedLink) {
      navigator.clipboard.writeText(generatedLink);
      setLinkCopied(true);
      toast.success('Lien copié !');
      setTimeout(() => setLinkCopied(false), 3000);
    }
  }, [generatedLink]);

  if (!waypoint) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-gray-900 border-gray-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5 text-[#f5a623]" />
            Partager le waypoint
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Partagez "{waypoint.name}" avec d'autres chasseurs BIONIC
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList className="bg-gray-800 border-gray-700 w-full">
            <TabsTrigger value="email" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Mail className="h-4 w-4 mr-1" />
              Email
            </TabsTrigger>
            <TabsTrigger value="link" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Link2 className="h-4 w-4 mr-1" />
              Lien
            </TabsTrigger>
            <TabsTrigger value="group" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Users className="h-4 w-4 mr-1" />
              Groupe
            </TabsTrigger>
          </TabsList>

          {/* Partage par Email */}
          <TabsContent value="email" className="space-y-4 mt-4">
            <div>
              <Label className="text-gray-300">Adresses email</Label>
              <Textarea
                value={emails}
                onChange={(e) => setEmails(e.target.value)}
                placeholder="email1@exemple.com, email2@exemple.com..."
                className="bg-gray-800 border-gray-700 text-white mt-1"
                rows={3}
              />
              <p className="text-xs text-gray-500 mt-1">
                Séparez les adresses par des virgules ou des retours à la ligne
              </p>
            </div>
            
            <div>
              <Label className="text-gray-300">Message (optionnel)</Label>
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ajoutez un message personnel..."
                className="bg-gray-800 border-gray-700 text-white mt-1"
                rows={2}
              />
            </div>
            
            <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3 text-xs text-blue-300">
              <p className="flex items-center gap-1"><Lightbulb className="h-3 w-3" /> Les destinataires recevront une notification et pourront modifier ce waypoint (collaboration complète)</p>
            </div>
            
            <Button 
              onClick={handleShareByEmail} 
              disabled={loading || !emails.trim()}
              className="w-full bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span> Envoi...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Send className="h-4 w-4" /> Envoyer les invitations
                </span>
              )}
            </Button>
          </TabsContent>

          {/* Partage par Lien */}
          <TabsContent value="link" className="space-y-4 mt-4">
            <div className="bg-gray-800/50 rounded-lg p-4 text-center">
              <Link2 className="h-12 w-12 mx-auto text-[#f5a623] mb-3" />
              <p className="text-sm text-gray-300 mb-4">
                Créez un lien unique que vous pouvez partager avec n'importe quel membre BIONIC
              </p>
              
              {generatedLink ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 bg-gray-900 rounded-lg p-2">
                    <Input 
                      value={generatedLink} 
                      readOnly 
                      className="bg-transparent border-0 text-xs text-gray-300"
                    />
                    <Button 
                      size="sm" 
                      variant="ghost"
                      onClick={copyLink}
                      className="text-[#f5a623]"
                    >
                      {linkCopied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500">
                    Ce lien expire dans 30 jours
                  </p>
                </div>
              ) : (
                <Button 
                  onClick={handleCreateLink}
                  disabled={loading}
                  className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
                >
                  <Link2 className="h-4 w-4 mr-2" />
                  Générer un lien de partage
                </Button>
              )}
            </div>
            
            <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3 text-xs text-amber-300">
              <p className="flex items-center gap-1"><Lock className="h-3 w-3" /> Seuls les membres BIONIC connectés peuvent accéder au waypoint via ce lien</p>
            </div>
          </TabsContent>

          {/* Partage avec Groupe */}
          <TabsContent value="group" className="space-y-4 mt-4">
            {allGroups.length > 0 ? (
              <>
                <div>
                  <Label className="text-gray-300">Sélectionner un groupe</Label>
                  <Select value={selectedGroupId} onValueChange={setSelectedGroupId}>
                    <SelectTrigger className="bg-gray-800 border-gray-700 text-white mt-1">
                      <SelectValue placeholder="Choisir un groupe..." />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      {allGroups.map(group => (
                        <SelectItem 
                          key={group.id} 
                          value={group.id}
                          className="text-white hover:bg-gray-700"
                        >
                          <span className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            {group.name}
                            <Badge variant="outline" className="text-xs">
                              {group.member_count} membres
                            </Badge>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="bg-green-900/30 border border-green-700/50 rounded-lg p-3 text-xs text-green-300">
                  <p className="flex items-center gap-1"><Users className="h-3 w-3" /> Tous les membres du groupe recevront une notification et pourront voir ce waypoint</p>
                </div>
                
                <Button 
                  onClick={handleShareWithGroup}
                  disabled={groupsLoading || !selectedGroupId}
                  className="w-full bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
                >
                  <Users className="h-4 w-4 mr-2" />
                  Partager avec le groupe
                </Button>
              </>
            ) : (
              <div className="text-center py-6">
                <Users className="h-12 w-12 mx-auto text-gray-600 mb-3" />
                <p className="text-gray-400 mb-4">Vous n'êtes membre d'aucun groupe</p>
                <Button 
                  variant="outline" 
                  className="border-[#f5a623] text-[#f5a623]"
                  onClick={() => {
                    onOpenChange(false);
                    // TODO: Ouvrir le dialog de création de groupe
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Créer un groupe de chasse
                </Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

/**
 * NotificationBell - Icône de notification avec badge
 */
export const NotificationBell = ({ count, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="relative p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-colors"
    >
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        className="h-5 w-5 text-gray-400"
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" 
        />
      </svg>
      {count > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
          {count > 9 ? '9+' : count}
        </span>
      )}
    </button>
  );
};

/**
 * CreateGroupDialog - Dialog de création de groupe
 */
export const CreateGroupDialog = ({ open, onOpenChange, userId, onCreated }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  
  const { createGroup, loading } = useHuntingGroups(userId);

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error('Entrez un nom de groupe');
      return;
    }
    
    const group = await createGroup(name, description, isPublic);
    if (group) {
      setName('');
      setDescription('');
      setIsPublic(false);
      onOpenChange(false);
      if (onCreated) onCreated(group);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-gray-900 border-gray-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-[#f5a623]" />
            Créer un groupe de chasse
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Rassemblez votre équipe pour partager vos spots
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div>
            <Label className="text-gray-300">Nom du groupe *</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Équipe Lac-Saint-Jean"
              className="bg-gray-800 border-gray-700 text-white mt-1"
              maxLength={50}
            />
          </div>
          
          <div>
            <Label className="text-gray-300">Description</Label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Décrivez votre groupe..."
              className="bg-gray-800 border-gray-700 text-white mt-1"
              rows={3}
              maxLength={500}
            />
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
            <div className="flex items-center gap-2">
              {isPublic ? (
                <Globe className="h-5 w-5 text-green-400" />
              ) : (
                <Lock className="h-5 w-5 text-yellow-400" />
              )}
              <div>
                <p className="text-sm font-medium">
                  {isPublic ? 'Groupe public' : 'Groupe privé'}
                </p>
                <p className="text-xs text-gray-500">
                  {isPublic 
                    ? 'Visible par tous, rejoindre librement'
                    : 'Sur invitation uniquement'
                  }
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsPublic(!isPublic)}
              className={`w-12 h-6 rounded-full transition-colors ${
                isPublic ? 'bg-green-500' : 'bg-gray-600'
              }`}
            >
              <span className={`block w-5 h-5 bg-white rounded-full transform transition-transform ${
                isPublic ? 'translate-x-6' : 'translate-x-0.5'
              }`} />
            </button>
          </div>
        </div>

        <DialogFooter className="mt-4">
          <Button 
            variant="outline" 
            onClick={() => onOpenChange(false)}
            className="border-gray-700"
          >
            Annuler
          </Button>
          <Button 
            onClick={handleCreate}
            disabled={loading || !name.trim()}
            className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
          >
            {loading ? 'Création...' : 'Créer le groupe'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ShareWaypointDialog;
