# Machine setup

Personal workstation and server setup, organized by the work each machine supports.

## Language

**Profile**:
The explicit set of capabilities selected for a machine. The workstation and server have separate profiles.
_Avoid_: Full setup, everything

**App group**:
A set of user-facing applications for one activity, such as browsing, notes, or 3D modeling. Membership expresses purpose rather than installation method.
_Avoid_: Flatpak group

**Tool group**:
A set of command-line tools for one activity, such as development, shell work, or container management.
_Avoid_: Core tools when development tools are included

**Server baseline**:
The capabilities declared in `server.md`, together with the prerequisites needed to support them. Extra services require an explicit change to that baseline.
_Avoid_: Homelab stack

**Managed setup**:
Installation and repeatable configuration owned by this repository.

**Enrollment**:
The account authorization, device pairing, or initial credential entry that connects an installed tool to the user's services.

**App lifecycle**:
Starting, stopping, restarting, or inspecting a deployed container app.
