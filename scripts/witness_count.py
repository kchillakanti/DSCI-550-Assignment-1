from number_parser import parse
import spacy
import re
import math
import numpy as np


nlp = spacy.load("en_core_web_sm")
def witness_count_main (df):
    def witness_count(description):
        # 1st stage: Initialize witness count & use number parser to parse description

        final_count = 0  # Initializing witness count
        parsed_description = parse(description)  # Using number parser to parse the description

        # 2nd stage: Use nlp, specifically spaCy to obtain estimate of witness count

        doc = nlp(parsed_description)  # Process the number-parsed description using spacy NLP
        valid_numbers = []  # List to store the valid numbers that represent count of witnesses in the description

        # Nouns that are not related to people in order to filter out the numbers that do not relate witness count
        non_people_nouns = ["shifts", "hours", "days", "years", "year", "minutes", "seconds", "months", "times",
                            "floor", "feet", "ghost", "ghosts", "spirit", "spirits"]

        # Verbs related to witnessing an event
        witness_verbs = ["witness", "hear", "see", "notice", "report", "describe", "experience"]

        for i, token in enumerate(doc):
            if token.like_num:  # like_num is an attribute in spacy. It returns true if the token resembles a number
                if i + 1 < len(doc):  # Checking if there is a next token to check
                    next_token = doc[i + 1]

                    # Checking if the next token next to the number is a Noun, specifically if it is a singular noun, plural noun or proper noun
                    if next_token.pos_ == 'NOUN' and next_token.tag_ in ['NNS', 'NNPS', 'NN']:
                        if next_token.text.lower() not in non_people_nouns:  # Ensuring that the next token after the number is not in the non_people_nouns
                            for j in range(i + 2, min(i + 5, len(doc))):  # Seeing the next few words as well
                                if doc[
                                    j].lemma_ in witness_verbs:  # Checking if the next few words are any of the verbs in the witness verbs list. .lemma takes the base form of the verb.
                                    try:
                                        valid_numbers.append(
                                            int(token.text))  # If there is a number, a token next to the number that is a noun and is not in the non_people_nouns list, and has a witness verb close by, then add the number to the valid numbers list
                                        break  # Once added to the valid numbers list break out of loop that checks for verbs
                                    except:  # Try and except used in case there are any conversion errors when doing int(token.text)
                                        break  # If we run into conversion errors, break out of the loop that checks for verbs and move on to the next number

                    # Checking if the next token after the number is a compound noun and not in non_people_nouns .dep checks the dependency between two words
                    if next_token.dep_ == "compound" and (next_token.head.text.lower() not in non_people_nouns):
                        for j in range(i + 2, min(i + 5, len(doc))):  # Again, iterating through the next few words after the noun to see if there is any verbs that are in the witness verbs list
                            if doc[j].lemma_ in witness_verbs:
                                try:
                                    valid_numbers.append(
                                        int(token.text))  # If conditions above are satisfied, the number is considered a valid number describing a witness count, and hence added to the valid numbers list
                                    break
                                except:
                                    break

        # 3rd stage: Use regex patterns to obtain estimate of witness count

        # Using regex pattern to search for specific witness count numbers in description
        number_of_witnesses = 0  # Now using a different method - using regex this time. Initializing the count of witnesses
        pattern_matching_specific_witness_count = "(\d+)\s+(\w+\s+\w+|\w+)\s+(have\s+seen|witnessed|have\s+witnessed|saw|observed|noticed|heard)"  # looking for specific witness count numbers here with this regex pattern
        specific_witness_count_matches = re.findall(pattern_matching_specific_witness_count, parsed_description)
        for match in specific_witness_count_matches:
            number_of_witnesses = number_of_witnesses + int(match[0])  # For every match, add to the number_of_witnesses

        if number_of_witnesses >= 10 and sum(valid_numbers) >= 10:  # If both numbers from both methods give a witness count greater than 10, those numbers are probably unreliable, so setting witness count to 0.
            final_count = 0

        elif number_of_witnesses >= 10 or sum(valid_numbers) >= 10:  # Assuming that it is unlikely that number of witnesses is greater than 10. If either value from either methods (regex and spacy nlp) gives a value greater than 10, it probably picked up an irrelevant number. Hence, taking the minimum out of the two.
            final_count = min(sum(valid_numbers), number_of_witnesses)

        else:
            final_count = (sum(valid_numbers) + number_of_witnesses) / 2  # Else, taking the average witness count of both the methods (regex and spacy nlp)


        # Using regex pattern to identify general words in description that might indicate witnesses
        pattern_matching_general_witness_count = "(several|many|few|people|others|some|witnesses|witness|person)?\s*\w*\s*(have said|were seen|have seen|have been seen|can be heard|have heard|saw|heard|hear|reported|witnessed|reports?|sightings?|incidents?|occurrences?)"
        general_witness_count_matches = re.findall(pattern_matching_general_witness_count,
                                                   parsed_description)  # Now I am checking for general words that imply witness. Not looking for specific number/count of witness

        if general_witness_count_matches and final_count == 0:  # If final count is still 0 based on previous steps, but we found some general words in the description that imply witness, set the witness count to the following:
            final_count = np.median(list(range(1,4)))  # Set final_count equal to the median of range between 1 and 4. This is a conservative range/approximation.

        elif general_witness_count_matches and final_count != 0:  # If final count is not equal to 0 based on previous steps, and we found some general words in the description that imply witness then perform the following:
            if isinstance(final_count, float) and final_count >= 1:  # If the final count is a float (due to average) and is greater than 1, then round down to nearest integer.
                final_count = math.floor(final_count)
            elif isinstance(final_count, float) and final_count < 1:  # If the final count is a float and is less than 1, then round up to nearest integer.
                final_count = math.ceil(final_count)
            final_count = np.median(list(range(final_count, final_count + 3)))  # As an approximation, set final_count equal to the median of the range between original final_count and original final_count + 3
            # For above line of code, I defined a conservative range, taking only the range between final_count and final_count+3
            # Thinking it might be better to underestimate than overestimate the witness count.


        if isinstance(final_count, float) and final_count >= 1:  # If final count greater than 1 and is of type float(due to average), round down to nearest integer.
            final_count = math.floor(final_count)
        elif isinstance(final_count, float) and final_count < 1:  # if final count is less than 1 and is of type float (due to average), round up to nearest integer.
            final_count = math.ceil(final_count)

        return final_count  # return final count

    haunted_places_df = pd.read_csv(df, sep="\t")
    haunted_places_df["witness count"] = haunted_places_df["description"].apply(witness_count)
    return haunted_places_df
