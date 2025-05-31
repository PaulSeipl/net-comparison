
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

interface InstallationServiceFilterProps {
  installationService: boolean | null;
  onInstallationServiceChange: (value: boolean | null) => void;
}

export const InstallationServiceFilter: React.FC<InstallationServiceFilterProps> = ({
  installationService,
  onInstallationServiceChange,
}) => {
  return (
    <Card>
      <CardHeader className="pb-2 p-4">
        <CardTitle className="text-sm">Installation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-4 pt-0">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="installation-required"
            checked={installationService === true}
            onCheckedChange={(checked) => 
              onInstallationServiceChange(checked ? true : null)
            }
          />
          <Label htmlFor="installation-required" className="text-sm">
            Installation erforderlich
          </Label>
        </div>
        
        <div className="flex items-center space-x-2">
          <Checkbox
            id="installation-not-required"
            checked={installationService === false}
            onCheckedChange={(checked) => 
              onInstallationServiceChange(checked ? false : null)
            }
          />
          <Label htmlFor="installation-not-required" className="text-sm">
            Keine Installation nötig
          </Label>
        </div>
        
        <div className="flex items-center space-x-2">
          <Checkbox
            id="installation-any"
            checked={installationService === null}
            onCheckedChange={(checked) => 
              onInstallationServiceChange(checked ? null : installationService)
            }
          />
          <Label htmlFor="installation-any" className="text-sm">
            Alle Angebote
          </Label>
        </div>
      </CardContent>
    </Card>
  );
};
