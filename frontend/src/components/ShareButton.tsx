
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Share, Copy, Check } from 'lucide-react';
import { NetworkRequestData, NormalizedOffer } from '@/types/api';
import { generateShareableUrl, getWhatsAppShareUrl } from '@/utils/urlState';
import { useToast } from '@/hooks/use-toast';

interface ShareButtonProps {
  searchData: NetworkRequestData;
  offers: NormalizedOffer[];
}

export const ShareButton: React.FC<ShareButtonProps> = ({ searchData, offers }) => {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const shareUrl = generateShareableUrl(searchData, offers);
  const whatsappUrl = getWhatsAppShareUrl(shareUrl, searchData);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      toast({
        title: "Link kopiert",
        description: "Der Freigabe-Link wurde in die Zwischenablage kopiert.",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: "Fehler",
        description: "Link konnte nicht kopiert werden.",
        variant: "destructive",
      });
    }
  };

  const openWhatsApp = () => {
    window.open(whatsappUrl, '_blank');
  };

  if (offers.length === 0) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center space-x-2">
          <Share className="w-4 h-4" />
          <span>Teilen</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={copyToClipboard} className="flex items-center space-x-2">
          {copied ? (
            <Check className="w-4 h-4 text-green-600" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
          <span>{copied ? 'Kopiert!' : 'Link kopieren'}</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={openWhatsApp} className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">W</span>
          </div>
          <span>WhatsApp teilen</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
