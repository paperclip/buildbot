from zope.interface import Interface, Attribute

class ISubscription(Interface):
    """
    A "thunk" representing a subscription to some event source;
    its only use is to cancel the subscription.
    """
    def cancel():
        """Cancel the subscription."""

class ISourceManager(Interface):
    """
    A source manager is responsible for:
     - monitoring a specific source-code repository, providing
       callbacks when the source changes.
     - producing a SourceStamp for the "current" state of the
       repository on demand
     - providing additional information about SourceStamps on
       demand (previous, blamelist, changes, affected files, etc.)

    All source manager classes must be subclasses of
    L{buildbot.framework.pools.PoolMember}.
    """

    def subscribeToChanges(callable):
        """
        Invoke the given callable in its own uthread with this
        L{ISourceManager} and an L{ISourceStamp} when any changes
        take place in the source-code repository::
            uthreads.spawn(callable(srcmanager, srcstamp))
        
        Returns an L{ISubscription}.
        """

    def getCurrentSourceStamp():
        """
        Get the L{ISourceStamp} for the current state of the
        repository.
        """

    # TODO: additional information

class ISourceStamp(Interface):
    """
    A SourceStamp represents, as accurately as possible, a specific
    "version" of the source code controlled by a L{ISourceManager}.
    The precise format depends on the version-control system in use
    by the L{ISourceManager}.
    """
    def getDescription():
        """
        Get a description of this SourceStamp that would allow a person
        to find the specified version.  The string may be arbitrarily long.
        """

    def getFilename():
        """
        Get a short string suitable for use in a filename that identifies
        this SourceStamp and has a minimal probability of clashing with
        any other SourceStamps.  Since that the SourceStamp is never 
        reconstructed from a filename, long SourceStamps can simply use a
        hash as the filename.
        """

class IScheduler(Interface):
    """
    A Scheduler starts builds.  It may do this by subscribing to a
    SourceManager, or by some kind of timer, or some other means.

    A scheduler's constructor should take, among other arguments:
     - action -- the function to call to start a build
     - context -- the context to pass to that function
    
    L{buildbot.framework.scheduler} provides convenient methods to
    implement a scheduler.
    """

class ISlave(Interface):
    """
    A Slave manages the connection from a remote machine.
    """

    def runCommand(command):
        """Run a command (L{buildbot.framework.interfaces.ICommand}) on
        the slave.  Returns a deferred which fires when the command
        completes, or fails if a Python exception occurs.  The command
        is responsible for collecting any more detailed information."""

class ICommand(Interface):
    """
    A command which can run on a buildslave, along with its immediate results.
    """

    # TODO temporary
    def run():
        """Do the thing; a microthreaded function"""

## History
#
# These interfaces represent the history of what Buildbot has done

class IHistoryManager(Interface):
    """
    A history manager is the central repository for accessing and modifying
    history.  This object is the starting point for all history operations,
    and serves as the root of the history element tree.

    Navigation of this tree is via microthreaded functions so that data
    can be loaded from backend storage systems without blocking.
    """

    def getElementByIdPath(path):
        """Get an arbitrary element by history element ID path.  Microthreaded function."""

    def getProjectNames():
        """Get a list of all project names.  Microthreaded function."""

    def getProject(name, create=False):
        """Get an IProjectHistory object, creating a new one if not found and
        create is True.  Microthreaded function."""

class IHistoryElt(Interface):
    """
    A generic history "element", which may be contained within another
    history element, and which may contain other history elements.  These
    elements structure the actions taken for a particular project into a
    tree, allowing users to "drill down" to see more detailed history.
    """

    historyEltId = Attribute("URL-safe name for the element")

    def getParentElt():
        """Get this object's parent IHistoryElt.  Microthreaded function."""

    def getChildElt(key):
        """Get the indicated child of this IHistoryElt; keys are arbitrary,
        short, URL-safe strings.  Microthreaded function."""

    def getChildEltKeys():
        """Return a list of keys for child elements of this IHistoryElt.
        Microthreaded function."""

    def getHistoryEltIdPath():
        """Return a tuple of strings which can be used to navigate from the
        buildmaster to this IHistoryElt.  The first item of the tuple names an
        IProjectHistory, and subsequent elements are keys to child elements.
        This tuple is intended to be serialized into a URL.  Microthreaded
        function.  """

    def newBuild(key):
        """Create a new object providing IBuildHistory.  Microthreaded function."""

    def newStep(key):
        """Create a new object providing IStepHistory.  Microthreaded function."""

class IProjectHistory(IHistoryElt):
    """
    A top-level container for all of the builds associated with a particular
    project.  A project has "shortcuts" to certain IHistoryElts that may be
    of interest to the user.
    """

    projectName = Attribute("Name of the project")

    # TODO: add methods

class IBuildHistory(IHistoryElt):
    """
    A build is an intermediate history element, mapping to the user's concept
    of a "build".  Note that builds may be children of other builds.
    """

    # TODO: add attributes - category, type
    # TODO: zero or more sourcestamps?
    # TODO: start/finish time?
    # TODO: status

class IStepHistory(IHistoryElt):
    """
    A step is an history element representing a single "operation" (from the
    user's perspective) in a build.  It may have logfiles, and may also have
    child history elements.
    """

    # TODO: blobs

    def newLogfile(name):
        """Create a new object providing IHistoryLogfile.  Microthreaded function."""

class IHistoryLogfile(Interface):
    """
    Represents some textual output from a buildstep
    """

    def getFilename():
        """get the filename of the logfile on disk"""