import React, { useEffect } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup'; // We'll need to add yup for schema validation
import * as yup from 'yup';
import {
  TextField,
  Button,
  Grid,
  Box,
  Typography,
  Paper,
  IconButton,
  FormHelperText,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
} from '@mui/material';
import { AddCircleOutline as AddIcon, DeleteOutline as DeleteIcon } from '@mui/icons-material';
import { Customer, CustomerFormData, QualityScore, VendorDetail } from '../../types/customer';

// TODO: Add yup to package.json: npm install yup @hookform/resolvers/yup
// For now, defining schema here. Could be moved to a separate validation file.
const qualityScoreSchema = yup.object().shape({
  metric_name: yup.string().required('Metric name is required'),
  score: yup.number().typeError('Score must be a number').required('Score is required').min(0).max(1000), // Adjust max as needed
  year: yup.number().nullable().typeError('Year must be a number').integer().min(1900).max(new Date().getFullYear() + 5),
  source: yup.string().nullable(),
});

const vendorDetailSchema = yup.object().shape({
  name: yup.string().required('Vendor name is required'),
  service_provided: yup.string().nullable(),
  notes: yup.string().nullable(),
});

const customerFormSchema = yup.object().shape({
  name: yup.string().required('Customer name is required').min(3, 'Name must be at least 3 characters'),
  description: yup.string().nullable(),
  business_model: yup.string().nullable(),
  membership_count: yup.number().nullable().typeError('Membership count must be a number').integer().min(0, 'Membership count cannot be negative'),
  website_url: yup.string().nullable().url('Must be a valid URL (e.g., http://example.com)'),
  primary_contact_name: yup.string().nullable(),
  primary_contact_email: yup.string().nullable().email('Must be a valid email address'),
  primary_contact_phone: yup.string().nullable(),
  notes: yup.string().nullable(),
  quality_scores: yup.array().of(qualityScoreSchema).nullable(),
  known_vendors: yup.array().of(vendorDetailSchema).nullable(),
});

interface CustomerFormProps {
  onSubmit: (data: CustomerFormData) => void;
  initialData?: Customer | null; // For editing
  isEditMode?: boolean;
  isLoading?: boolean;
}

const CustomerForm: React.FC<CustomerFormProps> = ({
  onSubmit,
  initialData,
  isEditMode = false,
  isLoading = false,
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CustomerFormData>({
    resolver: yupResolver(customerFormSchema),
    defaultValues: initialData
      ? {
          ...initialData,
          website_url: initialData.website_url || '', // Ensure empty string if null for URL type
          quality_scores: initialData.quality_scores || [],
          known_vendors: initialData.known_vendors || [],
        }
      : {
          name: '',
          description: '',
          business_model: '',
          membership_count: undefined, // Use undefined for optional numbers
          website_url: '',
          primary_contact_name: '',
          primary_contact_email: '',
          primary_contact_phone: '',
          notes: '',
          quality_scores: [],
          known_vendors: [],
        },
  });

  const { fields: qualityScoreFields, append: appendQualityScore, remove: removeQualityScore } = useFieldArray({
    control,
    name: 'quality_scores',
  });

  const { fields: vendorFields, append: appendVendor, remove: removeVendor } = useFieldArray({
    control,
    name: 'known_vendors',
  });

  useEffect(() => {
    if (initialData) {
      reset({
        ...initialData,
        website_url: initialData.website_url || '',
        quality_scores: initialData.quality_scores || [],
        known_vendors: initialData.known_vendors || [],
      });
    } else {
        reset({
            name: '', description: '', business_model: '', membership_count: undefined,
            website_url: '', primary_contact_name: '', primary_contact_email: '',
            primary_contact_phone: '', notes: '', quality_scores: [], known_vendors: [],
        });
    }
  }, [initialData, reset]);

  const businessModelOptions = ["HMO", "PPO", "EPO", "POS", "FFS", "Value-Based Care", "ACO", "Other"];


  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        {isEditMode ? 'Edit Customer' : 'Create New Customer'}
      </Typography>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Controller
              name="name"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Customer Name*" fullWidth error={!!errors.name} helperText={errors.name?.message} />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
             <FormControl fullWidth error={!!errors.business_model}>
                <InputLabel id="business-model-label">Business Model</InputLabel>
                <Controller
                    name="business_model"
                    control={control}
                    defaultValue=""
                    render={({ field }) => (
                        <Select {...field} labelId="business-model-label" label="Business Model">
                            <MenuItem value=""><em>None</em></MenuItem>
                            {businessModelOptions.map(option => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </Select>
                    )}
                />
                {errors.business_model && <FormHelperText>{errors.business_model.message}</FormHelperText>}
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <Controller
              name="description"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Description" fullWidth multiline rows={3} error={!!errors.description} helperText={errors.description?.message} />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Controller
              name="membership_count"
              control={control}
              render={({ field }) => (
                <TextField {...field} type="number" label="Membership Count" fullWidth error={!!errors.membership_count} helperText={errors.membership_count?.message}
                onChange={e => field.onChange(e.target.value === '' ? undefined : parseInt(e.target.value, 10))}
                />
              )}
            />
          </Grid>
           <Grid item xs={12} sm={6}>
            <Controller
              name="website_url"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Website URL" fullWidth error={!!errors.website_url} helperText={errors.website_url?.message} />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Controller
              name="primary_contact_name"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Primary Contact Name" fullWidth error={!!errors.primary_contact_name} helperText={errors.primary_contact_name?.message} />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Controller
              name="primary_contact_email"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Primary Contact Email" fullWidth error={!!errors.primary_contact_email} helperText={errors.primary_contact_email?.message} />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Controller
              name="primary_contact_phone"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Primary Contact Phone" fullWidth error={!!errors.primary_contact_phone} helperText={errors.primary_contact_phone?.message} />
              )}
            />
          </Grid>

          {/* Quality Scores Field Array */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Quality Scores</Typography>
            {qualityScoreFields.map((item, index) => (
              <Grid container spacing={2} key={item.id} sx={{ mb: 2, p:2, border: '1px solid #eee', borderRadius: 1}}>
                <Grid item xs={12} sm={4}>
                  <Controller
                    name={`quality_scores.${index}.metric_name`}
                    control={control}
                    render={({ field }) => <TextField {...field} label="Metric Name*" fullWidth error={!!errors.quality_scores?.[index]?.metric_name} helperText={errors.quality_scores?.[index]?.metric_name?.message} />}
                  />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Controller
                    name={`quality_scores.${index}.score`}
                    control={control}
                    render={({ field }) => <TextField {...field} type="number" label="Score*" fullWidth error={!!errors.quality_scores?.[index]?.score} helperText={errors.quality_scores?.[index]?.score?.message} />}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <Controller
                    name={`quality_scores.${index}.year`}
                    control={control}
                    render={({ field }) => <TextField {...field} type="number" label="Year" fullWidth error={!!errors.quality_scores?.[index]?.year} helperText={errors.quality_scores?.[index]?.year?.message} />}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <Controller
                    name={`quality_scores.${index}.source`}
                    control={control}
                    render={({ field }) => <TextField {...field} label="Source" fullWidth error={!!errors.quality_scores?.[index]?.source} helperText={errors.quality_scores?.[index]?.source?.message} />}
                  />
                </Grid>
                <Grid item xs={12} sm={1} sx={{display: 'flex', alignItems: 'center'}}>
                  <IconButton onClick={() => removeQualityScore(index)} color="error" aria-label="Remove quality score">
                    <DeleteIcon />
                  </IconButton>
                </Grid>
              </Grid>
            ))}
            <Button startIcon={<AddIcon />} onClick={() => appendQualityScore({ metric_name: '', score: 0, year: new Date().getFullYear(), source: '' })}>
              Add Quality Score
            </Button>
          </Grid>

          {/* Known Vendors Field Array */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Known Vendors</Typography>
            {vendorFields.map((item, index) => (
              <Grid container spacing={2} key={item.id} sx={{ mb: 2, p:2, border: '1px solid #eee', borderRadius: 1}}>
                <Grid item xs={12} sm={5}>
                  <Controller
                    name={`known_vendors.${index}.name`}
                    control={control}
                    render={({ field }) => <TextField {...field} label="Vendor Name*" fullWidth error={!!errors.known_vendors?.[index]?.name} helperText={errors.known_vendors?.[index]?.name?.message} />}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name={`known_vendors.${index}.service_provided`}
                    control={control}
                    render={({ field }) => <TextField {...field} label="Service Provided" fullWidth />}
                  />
                </Grid>
                {/* Notes for vendor could be a multiline textfield if needed */}
                <Grid item xs={12} sm={1} sx={{display: 'flex', alignItems: 'center'}}>
                  <IconButton onClick={() => removeVendor(index)} color="error" aria-label="Remove vendor">
                    <DeleteIcon />
                  </IconButton>
                </Grid>
                 <Grid item xs={12}>
                   <Controller
                    name={`known_vendors.${index}.notes`}
                    control={control}
                    render={({ field }) => <TextField {...field} label="Vendor Notes" fullWidth multiline rows={2}/>}
                  />
                </Grid>
              </Grid>
            ))}
            <Button startIcon={<AddIcon />} onClick={() => appendVendor({ name: '', service_provided: '', notes: '' })}>
              Add Vendor
            </Button>
          </Grid>

          <Grid item xs={12}>
            <Controller
              name="notes"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="General Notes" fullWidth multiline rows={4} error={!!errors.notes} helperText={errors.notes?.message} />
              )}
            />
          </Grid>

          <Grid item xs={12} sx={{ mt: 2 }}>
            <Button type="submit" variant="contained" color="primary" disabled={isLoading} sx={{ mr: 2 }}>
              {isLoading ? 'Saving...' : (isEditMode ? 'Save Changes' : 'Create Customer')}
            </Button>
            <Button type="button" variant="outlined" onClick={() => reset()} disabled={isLoading}>
              Reset Form
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default CustomerForm;
