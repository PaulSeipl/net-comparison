
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { ConnectionType } from '@/types/api';

interface ConnectionTypeFilterProps {
  connectionTypes: ConnectionType[];
  onConnectionTypeChange: (type: ConnectionType, checked: boolean) => void;
}

export const ConnectionTypeFilter: React.FC<ConnectionTypeFilterProps> = ({
  connectionTypes,
  onConnectionTypeChange,
}) => {
  const connectionTypeOptions: { value: ConnectionType; label: string }[] = [
    { value: 'Fiber', label: 'Glasfaser' },
    { value: 'Cable', label: 'Kabel' },
    { value: 'DSL', label: 'DSL' },
    { value: 'Mobile', label: 'Mobil' },
  ];

  return (
    <Card>
      <CardHeader className="pb-2 p-4">
        <CardTitle className="text-sm">Anschlussart</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-4 pt-0">
        {connectionTypeOptions.map((type) => (
          <div key={type.value} className="flex items-center space-x-2">
            <Checkbox
              id={`connection-${type.value}`}
              checked={connectionTypes.includes(type.value)}
              onCheckedChange={(checked) => onConnectionTypeChange(type.value, checked as boolean)}
            />
            <Label htmlFor={`connection-${type.value}`} className="text-sm">
              {type.label}
            </Label>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
