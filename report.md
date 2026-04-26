# Yarra Project Report: Working Lifecycle Across Modules

## 1. Introduction
This report outlines the functionality and user experience of the Yarra platform, a multi-tenant school management system. It details the working lifecycle for various user roles across all implemented modules, emphasizing the strict multi-tenancy and role-based access controls.

## 2. Global Features

### 2.1. Login & Logout
Users authenticate with their unique username and password. Upon successful login, they are redirected to their school's profile page. Logout functionality is available from the sidebar.
*   **User Roles**: All authenticated users.
*   **Access Control**: Standard Django authentication.
*   **Multi-tenancy**: Users are immediately associated with their school upon login.

[Screenshot: Login Page]
[Screenshot: Logout Confirmation (if applicable)]

### 2.2. Sidebar Navigation
The application features a modern, left-aligned sidebar navigation, providing quick access to all modules. The visibility of certain modules is dynamically controlled based on the user's role.
*   **User Roles**: All authenticated users.
*   **Access Control**: Modules like "Teachers Hub" and "Leadership Connect" are hidden from students and non-leaders, respectively.
*   **Multi-tenancy**: Displays the logged-in user's school logo and name, reinforcing their current context.

[Screenshot: Sidebar Navigation (Student View)]
[Screenshot: Sidebar Navigation (School Leader View)]

### 2.3. Notifications
A notification system is integrated into the top bar, showing recent updates and unread counts.
*   **User Roles**: All authenticated users.
*   **Access Control**: Notifications are personalized for the logged-in user.

[Screenshot: Notifications Dropdown]

## 3. Module: School Profile (GEMS Style)

This module provides a modern, visually appealing landing page for each school, showcasing its identity and key information.

### 3.1. School Leader / Admin Lifecycle (Edit Mode)
*   **View**: Can view their school's profile with comprehensive details.
*   **Edit**: Can click an "Edit School Profile" button to enter an edit mode.
*   **Update**: In edit mode, they can update school details such as name, location, contact information, key offerings, and upload a school logo. Changes are saved via a POST request.
*   **Access Control**: Only `school_leader` and `admin` roles can access the edit functionality.
*   **Multi-tenancy**: Can only edit the profile of their own associated school.

[Screenshot: School Profile - View Mode (School Leader)]
[Screenshot: School Profile - Edit Mode (School Leader)]

### 3.2. Other Roles Lifecycle (View Only)
*   **View**: Teachers and students can view their school's profile, but they do not have access to the edit functionality. The "Edit School Profile" button is not visible to them.
*   **Access Control**: Read-only access for `teacher`, `pl_teacher`, and `student` roles.
*   **Multi-tenancy**: Can only view the profile of their own associated school.

[Screenshot: School Profile - View Mode (Teacher/Student)]

## 4. Module: My Profile

This module allows all users to manage their personal and academic details in a structured, GEMS-style interface.

### 4.1. All Users Lifecycle (View & Edit)
*   **View**: Users can view their personal information, including basic details, academic information, addresses, and parent/guardian contacts.
*   **Edit**: Users can update most of their profile fields and upload a profile picture.
*   **Access Control**: Each user can only view and edit their own profile.
*   **Multi-tenancy**: Profile data is linked to the user and implicitly to their school.

[Screenshot: My Profile - ID Card Section]
[Screenshot: My Profile - Basic Information Section]
[Screenshot: My Profile - Academic Information Section]
[Screenshot: My Profile - Parent/Guardian Section]

## 5. Module: Competitions

This module allows schools to manage and students to register for various competitive events.

### 5.1. Student Lifecycle
*   **View Event List**: Can browse active competitions relevant to their school.
*   **View Event Detail**: Can view details of a specific competition, including brochure downloads and registration links.
*   **Register**: Can register for events (if applicable).
*   **Access Control**: Students only see events from their own school.
*   **Multi-tenancy**: Events are strictly filtered by the student's school.

[Screenshot: Competitions List (Student View)]
[Screenshot: Competition Detail Page (Student View)]

### 5.2. Teacher / PL Teacher Lifecycle
*   **View Event List**: Can browse active competitions for their school.
*   **View Event Detail**: Can view details of a specific competition.
*   **Access Control**: Teachers only see events from their own school.
*   **Multi-tenancy**: Events are strictly filtered by the teacher's school.

### 5.3. School Leader / Admin Lifecycle
*   **View Event List**: Can browse active competitions for their school.
*   **View Event Detail**: Can view details of a specific competition.
*   **Create Event**: Can create new competition events, which are automatically associated with their school.
*   **Edit Event**: Can edit existing competition events from their school.
*   **Add Results**: Can add competition results (winners, prizes) for events from their school.
*   **Access Control**: Can create/edit/add results only for events belonging to their school.
*   **Multi-tenancy**: Events are strictly filtered by the school leader/admin's school.

[Screenshot: Create Competition Event Form (School Leader/Admin)]
[Screenshot: Competition Detail with Add Result Form (School Leader/Admin)]

## 6. Module: Opportunities

Integrated with the Competitions module, this section highlights growth and development opportunities.

### 6.1. Student Lifecycle
*   **View Opportunity List**: Can browse active opportunities (e.g., scholarships, internships) relevant to their school.
*   **View Opportunity Detail**: Can view details of a specific opportunity.
*   **Access Control**: Students only see opportunities from their own school.
*   **Multi-tenancy**: Opportunities are strictly filtered by the student's school.

[Screenshot: Opportunities List (Student View)]

### 6.2. Teacher / PL Teacher Lifecycle
*   **View Opportunity List**: Can browse active opportunities for their school.
*   **View Opportunity Detail**: Can view details of a specific opportunity.
*   **Access Control**: Teachers only see opportunities from their own school.
*   **Multi-tenancy**: Opportunities are strictly filtered by the teacher's school.

### 6.3. School Leader / Admin Lifecycle
*   **View Opportunity List**: Can browse active opportunities for their school.
*   **View Opportunity Detail**: Can view details of a specific opportunity.
*   **Create Opportunity**: Can create new opportunities, automatically associated with their school.
*   **Edit Opportunity**: Can edit existing opportunities from their school.
*   **Access Control**: Can create/edit only for opportunities belonging to their school.
*   **Multi-tenancy**: Opportunities are strictly filtered by the school leader/admin's school.

## 7. Module: Teachers Hub

A private repository and meeting manager exclusively for staff members.

### 7.1. PL Teacher / Admin / School Leader Lifecycle (Upload & Manage)
*   **View Hub**: Can view all categorized resources (Upcoming Sessions, Past Recordings, Documents).
*   **Upload Resource**: Can upload new resources, including session details, recordings, or documents.
*   **Access Control**: Can upload resources.
*   **Multi-tenancy**: Can only manage resources for their own school.

[Screenshot: Teachers Hub - Upload Form (PL Teacher/Admin/School Leader)]

### 7.2. Teacher Lifecycle (View & Download)
*   **View Hub**: Can view all categorized resources (Upcoming Sessions, Past Recordings, Documents).
*   **Download**: Can download uploaded documents and access links for sessions/recordings.
*   **Access Control**: Cannot upload new resources.
*   **Multi-tenancy**: Can only view/download resources for their own school.

[Screenshot: Teachers Hub - Upcoming PL Sessions Section]
[Screenshot: Teachers Hub - Past Recordings Section]
[Screenshot: Teachers Hub - Resources (Documents) Section]

### 7.3. Student Lifecycle (Access Denied)
*   **Access Attempt**: Any attempt to access `/teachers-hub/` results in a 403 Forbidden error.
*   **Access Control**: Strictly denied access.

[Screenshot: Teachers Hub - Access Denied Page (Student)]

## 8. Module: School Network

This module acts as a global directory, allowing users to see information about all connected schools.

### 8.1. All Users Lifecycle (View Global Directory)
*   **View Network**: Can see a list of all schools in the Yarra network, including their logos, locations, and key offerings.
*   **Access Control**: View-only access to basic public information for all schools.
*   **Multi-tenancy**: This is the only module designed for cross-tenant visibility, but editing is restricted.

[Screenshot: School Network Page]

### 8.2. School Leader / Admin Lifecycle (Edit Own School)
*   **Edit Own School**: While viewing the global network, if they click on their own school's entry, they are redirected to their school's profile page where they can edit it (as described in Module 3).
*   **Access Control**: Cannot edit other schools' profiles.
*   **Multi-tenancy**: Editing is strictly limited to their own school.

## 9. Module: Leadership Connect

An exclusive forum for School Leaders and Administrators to discuss strategic topics.

### 9.1. School Leader / Admin Lifecycle (Create, Reply, Lock Thread)
*   **View Forum**: Can view a list of discussion threads.
*   **Create Thread**: Can initiate new discussion topics.
*   **Reply**: Can post replies to existing threads.
*   **Lock Thread**: The original author of a thread can add "Key Takeaways" and lock the thread, preventing further replies and creating a permanent summary.
*   **Access Control**: Exclusive access for `school_leader` and `admin` roles.
*   **Multi-tenancy**: Discussions are global across the leadership network, not school-specific.

[Screenshot: Leadership Connect - Discussion List]
[Screenshot: Leadership Connect - Thread Detail with Reply Form]
[Screenshot: Leadership Connect - Thread Detail with Lock/Summary Option (Author View)]

### 9.2. Other Roles Lifecycle (Access Denied)
*   **Access Attempt**: Any attempt to access `/leadership/` results in a 403 Forbidden error.
*   **Access Control**: Strictly denied access for `student`, `teacher`, and `pl_teacher` roles.

[Screenshot: Leadership Connect - Access Denied Page (Non-Leader)]
