# Search Marketplace Skill Delta Spec

## ADDED

### Matching Skills Returned as Detailed Cards
GIVEN a valid catalog URL and a query that matches one or more skill names or descriptions
WHEN `/superpowerwithcodex:search <query> --source <catalog-url>` is run
THEN each matching skill is displayed as a card showing name, description, author, and install command

### Case-Insensitive Matching
GIVEN a catalog with a skill whose name or description contains "TDD" in uppercase
WHEN the user searches with query "tdd" in lowercase
THEN the skill appears in the results

### No Results Message
GIVEN a valid catalog URL and a query that matches no skill names or descriptions
WHEN `/superpowerwithcodex:search <query> --source <catalog-url>` is run
THEN the output is exactly `No skills found for '<query>'` and no cards are shown

### Network Failure Error
GIVEN a catalog URL that is unreachable or returns a non-200 response
WHEN `/superpowerwithcodex:search <query> --source <catalog-url>` is run
THEN an error message is shown indicating the URL could not be reached

### Malformed Catalog Error
GIVEN a catalog URL that returns JSON without a `plugins[]` array
WHEN `/superpowerwithcodex:search <query> --source <catalog-url>` is run
THEN an error message is shown indicating unexpected catalog format at that URL

### Missing Query Usage Hint
GIVEN no query argument is provided
WHEN `/superpowerwithcodex:search --source <catalog-url>` is run
THEN the usage format is printed: `Usage: /superpowerwithcodex:search <query> --source <catalog-url>`
