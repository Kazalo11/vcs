import posixpath

from vcs.utils.lazy import LazyProperty

class NodeError(Exception):
    pass

class NodeKind:
    DIR = 1
    FILE = 2

class Node(object):
    """
    Simplest class representing file or directory on repository.

    We assert that if node's kind is DIR then it's url **MUST** have trailing
    slash (with one exception: root nodes have kind DIR but root node's url is
    always empty string) and FILE node's url **CANNOT** end with slash.
    Moreover, node's url cannot start with slash, too, as we oparete on
    *relative* paths only (this class is out of any context).
    """

    def __init__(self, url, kind):
        if url.startswith('/'):
            raise NodeError("Cannot initialize Node objects with slash at "
                "the beginning as only relative paths are supported")
        self.url = url
        self.kind = kind
        self.name = url.rstrip('/').split('/')[-1]
        self.dirs, self.files = [], []
        if self.is_root() and not self.is_dir():
            raise NodeError, "Root node cannot be FILE kind"

    @LazyProperty
    def parent(self):
        parent_url = self.get_parent_url()
        if parent_url:
            return Node(parent_url, NodeKind.DIR)
        return None

    def _get_kind(self):
        return self._kind

    def _set_kind(self, kind):
        if hasattr(self, '_kind'):
            raise NodeError, "Cannot change node's kind"
        else:
            self._kind = kind
            # Post setter check (url's trailing slash)
            if self.is_file() and self.url.endswith('/'):
                raise NodeError, "File nodes' urls cannot end with slash"
            elif not self.url=='' and self.is_dir() and \
                    not self.url.endswith('/'):
                raise NodeError, "Dir nodes' urls must end with slash"

    kind = property(_get_kind, _set_kind)

    def __cmp__(self, other):
        """
        Comparator using name of the node, needed for quick list sorting.
        """
        return cmp(self.name, other.name)

    def __eq__(self, other):
        for attr in self.__dict__:
            if self.__dict__[attr] != other.__dict__[attr]:
                return False
        return True

    def __nq__(self, other):
        return not self == other

    def __repr__(self):
        return '<Node %r>' % self.url

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    def get_name(url):
        """
        Returns name of the node so if its url
        then only last part is returned.
        """
        return url.split('/')[-1]

    def get_parent_url(self):
        """
        Returns node's parent url or empty string if node is root.
        """
        if self.is_root():
            return ''
        return posixpath.dirname(self.url.rstrip('/')) + '/'

    def is_file(self):
        """
        Returns ``True`` if node's kind is ``NodeKind.FILE``, ``False``
        otherwise.
        """
        return self.kind == NodeKind.FILE

    def is_dir(self):
        """
        Returns ``True`` if node's kind is ``NodeKind.DIR``, ``False``
        otherwise.
        """
        return self.kind == NodeKind.DIR

    def is_root(self):
        """
        Returns ``True`` if node is a root node and ``False`` otherwise.
        """
        return self.url == ''

    def get_mimetype(self, content):
        # Use chardet/python-magic/mimetypes?
        raise NotImplementedError

