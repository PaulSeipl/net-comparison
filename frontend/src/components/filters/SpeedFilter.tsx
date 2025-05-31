
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

interface SpeedFilterProps {
  speedRequirement: number;
  onSpeedRequirementChange: (speed: number) => void;
}

export const SpeedFilter: React.FC<SpeedFilterProps> = ({
  speedRequirement,
  onSpeedRequirementChange,
}) => {
  const speedOptions = [
    { value: 0, label: 'Alle Geschwindigkeiten' },
    { value: 25, label: 'Mindestens 25 Mbps' },
    { value: 50, label: 'Mindestens 50 Mbps' },
    { value: 100, label: 'Mindestens 100 Mbps' },
  ];

  return (
    <Card>
      <CardHeader className="pb-2 p-4">
        <CardTitle className="text-sm">Geschwindigkeit</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-4 pt-0">
        {speedOptions.map((option) => (
          <div key={option.value} className="flex items-center space-x-2">
            <Checkbox
              id={`speed-${option.value}`}
              checked={speedRequirement === option.value}
              onCheckedChange={() => onSpeedRequirementChange(option.value)}
            />
            <Label htmlFor={`speed-${option.value}`} className="text-sm">
              {option.label}
            </Label>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
