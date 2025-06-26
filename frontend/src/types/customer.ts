export interface VendorDetail {
  name: string;
  service_provided?: string | null;
  notes?: string | null;
}

export interface QualityScore {
  metric_name: string;
  score: number;
  year?: number | null;
  source?: string | null;
}

export interface CustomerBase {
  name: string;
  description?: string | null;
  business_model?: string | null; // e.g., HMO, PPO, Value-Based Care
  membership_count?: number | null;

  website_url?: string | null; // Input will be string, validated by Pydantic on backend
  primary_contact_name?: string | null;
  primary_contact_email?: string | null;
  primary_contact_phone?: string | null;

  notes?: string | null;
}

export interface Customer extends CustomerBase {
  id: number;
  created_at: string; // Typically string in ISO format from backend
  updated_at: string; // Typically string in ISO format from backend
  quality_scores: QualityScore[];
  known_vendors: VendorDetail[];
}

export interface CustomerCreate extends CustomerBase {
  quality_scores?: QualityScore[];
  known_vendors?: VendorDetail[];
}

// For CustomerUpdate, we can often reuse parts of CustomerCreate or define it more flexibly
// if only partial updates are allowed and all fields are optional.
// Pydantic's Update schema makes all fields optional, so we'll mirror that.
export interface CustomerUpdate {
  name?: string | null;
  description?: string | null;
  business_model?: string | null;
  membership_count?: number | null;
  website_url?: string | null;
  primary_contact_name?: string | null;
  primary_contact_email?: string | null;
  primary_contact_phone?: string | null;
  notes?: string | null;
  quality_scores?: QualityScore[] | null;
  known_vendors?: VendorDetail[] | null;
}

// For forms, it's often useful to have a type that matches the form structure
export type CustomerFormData = Omit<CustomerCreate, 'quality_scores' | 'known_vendors'> & {
  // For complex nested forms, these might need their own form data types
  quality_scores: QualityScore[];
  known_vendors: VendorDetail[];
};
