 CIS 422/522

### CIS 422/522 Software Methodologies  
Project 2 Evaluation Criteria

B. Norris - 2-16-2025

Most up-to-date version: https://github.com/UO-CS422/project2-template/blob/main/docs/ProjectEvaluation.md

Final projects should be delivered via GitHub. The following checklist is not complete but may help avoid some of the more obvious errors:

1.  **Completeness**: Make sure that every piece of the project is completed.
2.  **Consistency**: Where documents depend on one another, have the documents reviewed for consistency. For example, make sure that the User's Guide is consistent with the actual code delivered and with the requirements.
3.  **Application**: It is critical that you provide all of the instructions and links necessary for anyone to set up (if needed) and run your application. I suggest testing this on users who are completely naive to your project. The teaching staff cannot award points for code that they cannot run and will not have time to try to debug code or installation instructions.
4.  **Code**: Your final code submission must provide instructions on how to run the code so that it can be reviewed. Make sure that you have provided a README or equivalent describing the code structure and that the code is documented. In particular, be absolutely that any code that you have used from other sources (not written entirely yourself) is **clearly marked** to avoid any confusion over plagiarism issues. 
5.  **Processes**: All contributions should follow the development processes taught in class, including branch use, pull requests with reviews, testing, continuous integration and documentation. In addition, a `scrum` (or similarly named) subdirectory in your github repository must contain brief notes from all your scrum meetings, use the meeting date as the file name for each Scrum session.

Grading Overview
================

A total of 100 points are possible on each project, allocated as described in this document. Note that a single problem (e.g., inadequate documentation, or a program bug) can cost points in more than one category. For example, if the documentation is not adequate for using a feature, you won't get credit for implementing that feature, nor will you get credit for documenting a feature that doesn't actually work (you may instead lose points for inaccurate documentation). Likewise, if a feature is implemented but cannot be used because the program crashes, you won't get credit for implementing that feature.

15 - Initial Project Plan / SRS / SDS
=====================================

This initial deliverable for the project will be evaluated by assigning 0 to 1 point to each of the following fifteen bullets based on how well each was completed. Note that for Project 2, all of these items are required in your Feb 26 submission. One submission per team expected.

Document templates: https://classes.cs.uoregon.edu/25W/cs422/Templates.html

### Project Plan

*   A management plan. How is your team organized? How is the work divided among team members? How does your team make decisions? How will your team meet and how will it communicate.
*   Project milestones. Include at least 5 milestones that are specific, measurable, and time-bound.
*   Work breakdown structure. How is the project broken down into tasks? How are these tasks assigned to team members? Include at least 10 tasks and a corresponding Gantt chart (or similar timeline).
*   Monitoring and reporting: How individual and project progress will be monitored to keep track of who did what and when did they do it?
*   An implementation plan. At a high level, what is the sequence of steps you will take to implement the system? What intermediate prototypes are planned?
*   A rationale for the implementation plan. Why have you chosen these particular steps to build the system? What are your risks and your risk reduction strategies?  
    

### SRS

*   Problem statement - Clear and concisely, what is the problem to be solved? The problem, including the task requirements, should be described independently of the solution, the piece of software you will build.
*   Description of User - Who are the users? What will they expect? What will they know already? What are their current technology usage patterns?
*   Scenarios or Use Cases - Three specific, different, realistic scenarios.
*   Detailed Description of Requirements - Expand the problem statement and generalize from the use cases. Include at least 20 specific and measurable requirements. At least 6 should be non-functional requirements.
*   Both functional and non-functional requirements should be split between _absolutely required_ and _not absolutely required_ requirements. A reasonable number of _absolutely required_ requirements are identified, well-specified but attainable.

### SDS

Note that for the first project submission, you are submitting an initial design, which is expected to continue to evolve as you work on the project. To that end, it does not have to include UML diagrams yet, but they must be present in your final project submission.

*   A description of the product you intend to build. This should describe the externally visible behavior of your product as precisely as possible, but it should be concise and clear.
*   An overall design description. What are the major parts of your system, and how do they fit together?
*   System structure is clear.
*   Each major subsystem should be explained using a separate static model and dynamic model. All diagrams must be clear and understandable.
*   Design Rationale. Why did you chose this particular design? What are the main organizing principles that you used to break your system into parts?

### Good Writing

Throughout all sections: Good Writing (From Syllabus) Structure the paper so that the main ideas are clearly accessible. Communicate individual ideas effectively. All spelling and grammar must be standard and correct.


40 - Application Quality
========================

Application quality includes features used by all categories of user. Often this includes administrative users (sysadmins, etc.) in addition to end users. Functionality also includes performance and scalability.

### Robustness: 10

This evaluates the extent to which the system can be run with no bugs or errors, such as by failing to install and compile, by behaving differently than specified, or by crashing. 

### Feature Set: 10

This evaluates the extent to which the system exceeded, met, or fell short of requirements. This considers requirements that were assigned and specified by the team. This evaluates whether essential features were missing and whether extended features were provided.

### Ease of Use: 10

This category includes setup (if any) as well as usability for end users and for administrators. It is typically distinct from quality of documentation, but may include presence and usefulness of online help. Usability considerations for administrative users may be quite different than usability considerations for end users; both are considered here. For a prototype, this addresses both existing and planned features.

### User Documentation Including Installation and Setup: 10

This evaluates the extent to which documentation clearly and accurately describes, for an end-user, how to accomplish,real-world tasks using the software. This includes how to install and set up the system. The documentation should be clear, accurate, well-written, well-organized, and complete.

It's recommended to include this documentation in the `README.md` file in your repository, but you may 
also include it in an additional separate user guide document in the `docs` directory -- if you do, be sure to include a pointer to it in the `README.md` file.

45 - Organization, Planning and Technical Documentation
=======================================================

Technical documentation and system organization are evaluated together. Good documentation can make a good design evident, and poor documentation can doom a good design to degradation over time, but good documentation cannot compensate for poor design.

### Project Management Final Report: 10 points

This section is evaluated on how effectively the team preforms project planning, how well it followed the plan, how well the team adapts the plan to inevitable hiccups, and whether risks are effectively considered, mitigated, and re-evaluated when plans change. While you should primarily use GitHub project boards, issues, and pull requests to track progress, summarize the main changes to your plans in this section.

For full points, include the GitHub project's "Table" view of your tasks, which includes "Title", "Assignees", and "Status" columns. There should be at least 12 tasks (no upper limit).  Also include a screenshot of your GitHub projects "Roadmap" view with the final Gantt chart for your project.

In your `docs/ScrumNotes.md` file, maintain a clear record of when meetings were held, and what was accomplished and agreed upon at each meeting. Include a brief summary of what was discussed at each Scrum meeting in the `scrum` subdirectory of your repository.

All contributions should follow recommended git practices (tutorial: https://youtu.be/_wQdY_5Tb5Q). Code reviews should be conducted for all pull requests prior to merging.

### Final Systems Requirements (SRS) - 5 points

This should include all elements described in the initial SRS submission, **updated** to reflect what was actually built. This should include a clear, complete, and well-organized description of requirements, including a rationale for what is included, what has been deferred to the future, and (as appropriate) what has been excluded. The document should provide a clear user-centric specification as well as a well-defined, precise technical specification. Future developers should be able to use the document for system creation or maintenance.

### Final System Architecture and Design Documentation - 10 points

The software design is communicated as follows:

*   Software Architecture: This section should describe the software structure by answering the following questions for a reader:
    *   How is the software decomposed into components?
    *   How do the components work together to implement the most important application features?
*   Why was this particular design chosen? What is the rationale for any key design decisions? 
*   Testing strategy: what types of tests are included and how they are used to validate the system.

This section should provide an easily understandable specification of the system architecture. Key architectural design decisions should be communicated, along with the rationale for each. The design should satisfy stated design goals.

### Implementation Documentation - 5 points

This evaluates the documentation in the software implementation itself. This includes:
* Coding style: https://classes.cs.uoregon.edu/25W/cs422/coding_style.html
* Automatically generated documentation, e.g., pydoc, doxygen, jsdoc, etc. This should be present in your repository in the `docs/html` subdirectory and should include all modules, classes, and methods.

### Testing and Continuous Integration - 10 points

This evaluates the extend to which testing and CI were used in the project. 
*  Testing: The project should include a test suite that tests the functionality of the system. The test suite should be well-organized and should include both unit tests and integration tests.
*  The test suite should be run automatically by a CI system.

### Class Presentation - 5 points

The presentation should clearly and accurately convey key lessons learned and the application of lessons from class.

Modified bt B. Norris, 2/16/25. Created by A.Hornof, 4/24/18. Adapted from materials created by Stuart Faulk Michal Young.  
