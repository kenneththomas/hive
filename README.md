# HIVE/DUMFIX

# Mission
HIVE is a Trading Engine that is being built to contain much of the logic of a real FIX engine. It will take DUMFIX as input, undergo standard order management procedures including risk checking and exchange slicing.

DUMFIX is based off of the FIX 4.2 protocol. Like the name implies, it&#39;s a dumbed down version of FIX. I&#39;m working on this as a personal project to play around with, but perhaps it could evolve into a way to gain a basic understanding of FIX protocol.

The reason why I&#39;m &quot;creating&quot; DUMFIX is because I&#39;m attempting to code extremely crude versions of trading engines that I&#39;ve worked with throughout my career. I&#39;m doing this for fun, so I want to ignore all of the less fun overhead parts of FIX protocol.

The most important aspects of DUMFIX is that it will be:

- Sessionless, DUMFIX engines will not care about logons, sequence numbers, and sendercomp/targetcomp will mostly only be used here for decoration.
- Less required tags – body length, sequence number, any time-related tags will largely be ignored by DUMFIX engines.
- Containing the same tags as FIX 4.2; while less tags are required and not all tags are guaranteed to be processed, the tags will "mean" the same thing regardless.

The most important aspect of DUMFIX is understanding input/output.

# About the Author

I don&#39;t have a formal computer science background, but I do have a finance background and a keen interest in electronic trading from the technology perspective. I have been working with FIX 4.2 in a project management, testing, and client certification role. While I feel I do excel in the organization and presentational aspects of my job, I want to improve my scripting and programming skills as well.