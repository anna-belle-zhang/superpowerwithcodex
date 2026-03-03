# Greeter Delta Spec

## ADDED

### Personalized Greeting
GIVEN a name string that is not empty
WHEN `greeter` is called with that name
THEN it returns a greeting string that includes the provided name

### Default Greeting for Empty Name
GIVEN an empty string is provided as the name
WHEN `greeter` is called
THEN it returns a default greeting that does not include any name
