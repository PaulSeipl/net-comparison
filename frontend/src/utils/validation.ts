
import { addressService } from '@/services/addressService';

export interface ValidationErrors {
  street?: string;
  houseNumber?: string;
  zip?: string;
  city?: string;
  address?: string;
}

export const validateSearchForm = (formData: {
  street: string;
  houseNumber: string;
  zip: string;
  city: string;
}): ValidationErrors => {
  const errors: ValidationErrors = {};

  // Street validation
  if (!formData.street.trim()) {
    errors.street = 'Straße ist erforderlich';
  } else if (formData.street.trim().length < 2) {
    errors.street = 'Straße muss mindestens 2 Zeichen haben';
  }

  // House number validation
  if (!formData.houseNumber.trim()) {
    errors.houseNumber = 'Hausnummer ist erforderlich';
  } else if (!addressService.validateHouseNumber(formData.houseNumber)) {
    errors.houseNumber = 'Ungültige Hausnummer (z.B. 5, 5a, 5-7)';
  }

  // ZIP code validation
  if (!formData.zip.trim()) {
    errors.zip = 'PLZ ist erforderlich';
  } else if (!addressService.validateGermanZip(formData.zip)) {
    errors.zip = 'PLZ muss 5 Ziffern haben';
  }

  // City validation
  if (!formData.city.trim()) {
    errors.city = 'Stadt ist erforderlich';
  } else if (formData.city.trim().length < 2) {
    errors.city = 'Stadt muss mindestens 2 Zeichen haben';
  }

  return errors;
};

export const validateEmail = (email: string): string | null => {
  if (!email) return 'E-Mail ist erforderlich';
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Ungültige E-Mail-Adresse';
  }
  
  return null;
};

export const validatePhone = (phone: string): string | null => {
  if (!phone) return null; // Phone is optional
  
  // German phone number validation (basic)
  const phoneRegex = /^(\+49|0)[1-9]\d{1,14}$/;
  if (!phoneRegex.test(phone.replace(/[\s-]/g, ''))) {
    return 'Ungültige Telefonnummer';
  }
  
  return null;
};
