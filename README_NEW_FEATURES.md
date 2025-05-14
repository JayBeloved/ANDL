# New Features: Subcategories and Quotes

This document outlines the new features added to the Apostle Niyi Digital Library application.

## 1. Subcategories Feature

The subcategories feature allows for a hierarchical organization of content. Categories can now have subcategories, providing a more structured way to organize and browse content.

### How to Use Subcategories

1. **Creating Subcategories**:
   - In the admin panel, navigate to the "Sub Categories" section
   - Click "Add Sub Category"
   - Fill in the name, description, select a parent category, and optionally upload an image
   - Save the subcategory

2. **Assigning Content to Subcategories**:
   - When creating or editing content, you can now select both a category and a subcategory
   - The subcategory dropdown will only show subcategories belonging to the selected category

3. **Browsing Subcategories**:
   - On the category page, all subcategories are displayed as cards
   - Users can click on a subcategory to view content specific to that subcategory
   - The navigation breadcrumb shows the hierarchy: Home > Category > Subcategory

## 2. Quotes Feature

The quotes feature allows for creating and sharing inspirational quotes in a Pinterest-style board layout. Users can customize the background and share quotes on social media.

### How to Use Quotes

1. **Creating Quotes**:
   - First, create a new Content with the content type set to "Quote"
   - After saving the content, go to the "Quotes" section in the admin panel
   - Click "Add Quote"
   - Select the quote content you just created
   - Enter the quote text
   - Upload background images (up to 5 different backgrounds)
   - Select a default background
   - Save the quote

2. **Viewing Quotes**:
   - Users can browse all quotes on the dedicated Quotes page
   - Quotes are displayed in a Pinterest-style masonry grid
   - Each quote shows the quote text, author, and has View and Share buttons

3. **Sharing Quotes**:
   - When viewing a quote, users can click the "Share This Quote" button
   - On the share page, users can:
     - Choose from up to 5 different backgrounds
     - Generate an image with the quote text, author name, and website
     - Download the generated image
     - Share directly to Facebook, Twitter, WhatsApp, or Instagram

## Implementation Details

### New Models

1. **SubCategory Model**:
   - Related to a parent Category
   - Has name, description, slug, and image fields
   - Linked to Content through a ForeignKey relationship

2. **Quote Model**:
   - Related to a Content object (of type 'QUOTE')
   - Contains the quote text
   - Has fields for 5 different background images
   - Tracks share count

### New Views

1. **SubCategoryView**:
   - Displays content filtered by both category and subcategory
   - Shows other subcategories in the same category

2. **QuoteListView**:
   - Displays all quotes in a Pinterest-style grid

3. **QuoteShareView**:
   - Allows users to select a background and generate a shareable image
   - Provides options to download or share the image

4. **generate_quote_image**:
   - API endpoint that generates the quote image with the selected background
   - Adds the quote text, author name, and website to the image
   - Returns the image as a base64-encoded string

### New Templates

1. **subcategory.html**:
   - Displays content within a specific subcategory
   - Shows other subcategories in the same category

2. **quotes.html**:
   - Pinterest-style grid layout for quotes
   - Responsive design that works on all device sizes

3. **quote_share.html**:
   - Interface for selecting backgrounds and sharing quotes
   - Preview of the generated quote image
   - Buttons for downloading and sharing to social media

## Migration

A migration file (`0002_add_subcategory_and_quote_models.py`) has been created to add the new models and fields to the database. Run the migration with:

```
python manage.py migrate
```

## Additional Notes

- The quote sharing feature requires the Pillow library for image manipulation
- For production, you should include font files in your project for the quote text rendering
- Social media sharing uses standard web sharing APIs, which may have limitations on some platforms (especially Instagram)