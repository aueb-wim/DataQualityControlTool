from collections import namedtuple

Replacement = namedtuple('Replacement', ['source', 'target'])


def ifstr(columnname, repls):
    """Returns a mipmap function string with encapsulated if statements 
    for replacing given values of a column with predefined ones. 
    This is used in a categorical/nominal column type

    Arguments:
    :param columnname: the column name(str)
    :param repls: list with Replacement namedtuples
                  Replacement('source', 'target')   
    """
    local_repls = repls.copy()
    if len(repls) == 1:
        return 'if({} == \"{}\", \"{}\", null())'.format(columnname, repls[0].source, repls[0].target)
    elif len(repls) > 1:
        current = local_repls.pop(0)
        return 'if({} == \"{}\", \"{}\", {})'.format(columnname,
                                                     current.source,
                                                     current.target,
                                                     ifstr(columnname, local_repls))
