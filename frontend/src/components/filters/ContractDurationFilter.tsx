
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

interface ContractDurationFilterProps {
  contractDuration: number[];
  onContractDurationChange: (duration: number, checked: boolean) => void;
}

export const ContractDurationFilter: React.FC<ContractDurationFilterProps> = ({
  contractDuration,
  onContractDurationChange,
}) => {
  const contractOptions = [
    { value: 12, label: '12 Monate' },
    { value: 24, label: '24 Monate' },
    { value: 36, label: '36 Monate' },
  ];

  return (
    <Card>
      <CardHeader className="pb-2 p-4">
        <CardTitle className="text-sm">Vertragslaufzeit</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-4 pt-0">
        {contractOptions.map((option) => (
          <div key={option.value} className="flex items-center space-x-2">
            <Checkbox
              id={`contract-${option.value}`}
              checked={contractDuration.includes(option.value)}
              onCheckedChange={(checked) => onContractDurationChange(option.value, checked as boolean)}
            />
            <Label htmlFor={`contract-${option.value}`} className="text-sm">
              {option.label}
            </Label>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
