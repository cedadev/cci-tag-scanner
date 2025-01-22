# Notes for removing triple store

## SPARQL Query requests:

### get_concepts_in_scheme

From all items, verify in scheme, pull out ID and verify in endpoints list, then get prefLabel.

### get_alt_concepts_in_scheme

From all items, verify in scheme, pull out ID and verify in endpoints list, then get altLabel.

### get_broader

Does something interesting with a request for 'narrower'

### get_alt_label

Links to get nerc or get ceda alt_label. Still just getting alt or pref labels.

## Facet Object Components

### __facets private attribute
 - `facets[facet]` = dict of concepts arranged by label/concept (@value - prefLabel/@id)
 - `facets[facet-alt]` = same as above but with (@value - altLabel/@id)
 - `facets[broader-processing-level]` = get alt level for proc level mappings.

## __proc_level_mappings
 - `proc_level_mappings[proc_level.uri]` - @id from above facet = single item(concept) from records that contain a 'narrower' option.

## __platform_program_mappings
 - `platform_program_mappings[platform.uri]` - @id from above facet = single item(label) from records that contain a 'narrower' option.

## __programme_group_mappings
 - `programme_group_mappings[single item(concept)]` - from above = single item(label) from other records that contain a 'narrower' option.

## __reversible_facet_mappings
 - Reversed mappings for each facet, makes construction of mappings easier.

## FACET_ENDPOINTS
 - Defined config values

## LABEL_SOURCE
 - Defined config values