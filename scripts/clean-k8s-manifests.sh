#!/bin/bash
######################################################################
# Clean Kubernetes Manifests Script
# 
# This script removes runtime metadata from exported Kubernetes YAML
# manifests to make them suitable for version control and redeployment.
#
# Usage: ./clean-k8s-manifests.sh <directory>
# Example: ./clean-k8s-manifests.sh exported-manifests/
######################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "$1"
}

# Check if directory argument is provided
if [ $# -eq 0 ]; then
    print_error "No directory specified"
    echo "Usage: $0 <directory>"
    echo "Example: $0 exported-manifests/"
    exit 1
fi

MANIFEST_DIR="$1"

# Check if directory exists
if [ ! -d "$MANIFEST_DIR" ]; then
    print_error "Directory '$MANIFEST_DIR' does not exist"
    exit 1
fi

# Check if directory contains any YAML files
YAML_FILES=("$MANIFEST_DIR"/*.yaml "$MANIFEST_DIR"/*.yml)
if [ ! -e "${YAML_FILES[0]}" ] && [ ! -e "${YAML_FILES[1]}" ]; then
    print_error "No YAML files found in '$MANIFEST_DIR'"
    exit 1
fi

print_info "Starting cleanup of Kubernetes manifests in: $MANIFEST_DIR"
print_info "================================================"

# Counter for processed files
processed=0
skipped=0

# Process each YAML file
for file in "$MANIFEST_DIR"/*.{yaml,yml}; do
    # Skip if file doesn't exist (handles no match case)
    [ -e "$file" ] || continue
    
    filename=$(basename "$file")
    print_info "\nProcessing: $filename"
    
    # Create a backup
    cp "$file" "$file.backup"
    
    # Use yq if available, otherwise use sed
    if command -v yq &> /dev/null; then
        print_info "  Using yq for cleaning..."
        
        # Remove runtime metadata fields using yq
        yq eval 'del(.metadata.resourceVersion,
                     .metadata.uid,
                     .metadata.selfLink,
                     .metadata.creationTimestamp,
                     .metadata.generation,
                     .metadata.managedFields,
                     .metadata.namespace,
                     .status)' -i "$file"
        
        # Clean up kubectl annotations if they exist
        yq eval 'del(.metadata.annotations."kubectl.kubernetes.io/last-applied-configuration")' -i "$file"
        
        # Remove empty metadata.annotations object if it exists
        yq eval 'del(.metadata.annotations | select(. == {}))' -i "$file"
        
    else
        print_warning "  yq not found, using sed (less precise)..."
        
        # Create a temporary file
        temp_file=$(mktemp)
        
        # Use awk to remove specific fields and the entire status section
        awk '
        BEGIN { in_status=0; in_managed_fields=0; skip_line=0 }
        
        # Skip status section
        /^status:/ { in_status=1; next }
        in_status && /^[a-zA-Z]/ { in_status=0 }
        in_status { next }
        
        # Skip managedFields section
        /^  managedFields:/ { in_managed_fields=1; next }
        in_managed_fields && /^  [a-zA-Z]/ { in_managed_fields=0 }
        in_managed_fields { next }
        
        # Skip specific metadata fields
        /^  resourceVersion:/ { next }
        /^  uid:/ { next }
        /^  selfLink:/ { next }
        /^  creationTimestamp:/ { next }
        /^  generation:/ { next }
        /^  namespace: default/ { next }
        
        # Skip kubectl last-applied-configuration annotation
        /kubectl.kubernetes.io\/last-applied-configuration/ { skip_line=1; next }
        skip_line && /^    [a-zA-Z]/ { skip_line=0 }
        skip_line { next }
        
        # Print all other lines
        { print }
        ' "$file" > "$temp_file"
        
        mv "$temp_file" "$file"
    fi
    
    # Check if file was modified
    if ! cmp -s "$file" "$file.backup"; then
        print_success "  Cleaned: $filename"
        processed=$((processed + 1))
    else
        print_warning "  No changes: $filename"
        skipped=$((skipped + 1))
    fi
    
    # Remove backup if cleaning was successful
    rm "$file.backup"
done

print_info "\n================================================"
print_info "Cleanup Summary:"
print_success "  Files processed: $processed"
if [ $skipped -gt 0 ]; then
    print_warning "  Files skipped (no changes): $skipped"
fi

print_info "\nVerifying cleaned manifests..."
# Verify YAML syntax
errors=0
for file in "$MANIFEST_DIR"/*.{yaml,yml}; do
    [ -e "$file" ] || continue
    
    if command -v yq &> /dev/null; then
        if ! yq eval '.' "$file" > /dev/null 2>&1; then
            print_error "  Invalid YAML: $(basename "$file")"
            errors=$((errors + 1))
        fi
    else
        # Basic syntax check using python if yq is not available
        if command -v python3 &> /dev/null; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                print_error "  Invalid YAML: $(basename "$file")"
                errors=$((errors + 1))
            fi
        fi
    fi
done

if [ $errors -eq 0 ]; then
    print_success "All manifests are valid YAML"
else
    print_error "$errors manifest(s) have YAML syntax errors"
    exit 1
fi

print_info "\n================================================"
print_success "Cleanup completed successfully!"
print_info "\nNext steps:"
print_info "1. Review the cleaned manifests in: $MANIFEST_DIR"
print_info "2. Test with: kubectl apply -f $MANIFEST_DIR --dry-run=client"
print_info "3. Copy to repository: cp $MANIFEST_DIR/*.yaml k8s/postgresql/"
print_info "4. Commit: git add k8s/postgresql/ && git commit -m 'Update PostgreSQL manifests'"

exit 0