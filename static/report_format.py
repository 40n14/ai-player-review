"""Names and markers shared by the report readers and writers."""

import json
import os
import re
from functools import lru_cache
from pathlib import Path


LANGUAGES = ('zh', 'en')
SECTIONS = {
    '玩家反馈': ('Player feedback', 'Player feedback summary'),
    '上一轮反馈的去向': ('Follow-up on last round',),
    '结论': ('Conclusion',),
}
CONFIDENCE = re.compile(
    r'(?:把握|Confidence)\*{0,2}[：:]\s*\**(【[^】]+】|'
    r'\[(?:Confirmed|Possible|Design|Definitely missing|Possibly missing|Inferred|Regression)\])',
    re.I,
)
CHECK = re.compile(r'^\s*[-*]\s*\**(?:核对|Verification)\**[：:]\s*\**(.+)$', re.I | re.M)


@lru_cache(maxsize=1)
def localized_files():
    path = Path(__file__).resolve().parents[1] / 'api' / 'texts.json'
    with path.open(encoding='utf-8-sig') as f:
        return json.load(f)['files']


def language(project):
    return 'en' if (project or {}).get('language') == 'en' else 'zh'


def names(project, kind):
    """A configured name first, then the two defaults in project-language order."""
    override = ((project or {}).get('reportNames') or {}).get(kind)
    pair = localized_files()[kind]
    options = [pair[language(project)], pair['zh' if language(project) == 'en' else 'en']]
    return tuple(dict.fromkeys(([override] if override else []) + options))


def named_path(project, folder, kind, *, write=False):
    paths = [os.path.join(folder, n) for n in names(project, kind)]
    if not write:
        return next((p for p in paths if os.path.exists(p)), paths[0])
    return paths[0]


def is_merged(name, project=None):
    patterns = names(project, 'groupMerged')
    return (name in names(project, 'merged') or '合并' in name or
            any(re.fullmatch(re.escape(p).replace(r'\{0\}', '.+'), name, re.I) for p in patterns))


def is_review_markdown(name, project=None):
    if (not name.lower().endswith('.md') or name.startswith(('_', 'task_'))
            or name.lower() in ('review.md', 'player-feedback.md', '玩家反馈.md')
            or '草稿' in name or name.lower().endswith('.draft.md') or name in names(project, 'cost')):
        return False
    for proposal in names(project, 'expand'):
        stem, ext = os.path.splitext(os.path.basename(proposal))
        if name == stem + ext or (name.startswith(stem + '_') and name.endswith(ext)):
            return False
    return True


def report_aliases(project, name):
    """Equivalent built-in report names, including the old localized split labels."""
    if name in names(project, 'merged'):
        return names(project, 'merged')
    patterns = names(project, 'groupMerged')
    for pattern in patterns:
        merged = re.fullmatch(re.escape(pattern).replace(r'\{0\}', '(.+)'), name, re.I)
        if merged and merged.lastindex:
            return tuple(dict.fromkeys(n.format(merged[1]) for n in patterns))
    group = re.fullmatch(r'(?:玩家视角审查_|player-review_)(.+)\.md', name)
    if not group:
        return (name,)
    part = group[1]
    zh, en = part, part
    config = (project or {}).get('reportNames') or {}
    explicit = config.get('group')
    overrides = [explicit.format(part)] if explicit and '{0}' in explicit else []
    for split in (project or {}).get('characterSplits') or ():
        sid, label = split.get('id'), split.get('name')
        if sid and label and part.endswith(('_' + sid, '_' + label)):
            base = part.rsplit('_' + (sid if part.endswith('_' + sid) else label), 1)[0]
            zh, en = base + '_' + label, base + '_' + sid
            pattern = config.get('split') or (explicit.replace('{0}', '{0}_{1}') if explicit else '')
            overrides = [pattern.format(base, label)] if pattern else []
            break
    options = ['玩家视角审查_%s.md' % zh, 'player-review_%s.md' % en]
    if language(project) == 'en':
        options.reverse()
    return tuple(dict.fromkeys(overrides + options + [name]))


def existing_reports(folder, project, blocked=lambda path: False):
    if blocked(folder):
        return []
    result = []
    for name in sorted(os.listdir(folder)):
        if is_review_markdown(name, project):
            aliases = report_aliases(project, name)
            path = next((os.path.join(folder, n) for n in aliases
                         if not blocked(os.path.join(folder, n)) and os.path.isfile(os.path.join(folder, n))), None)
            if path and path not in result:
                result.append(path)
    return result


def filename_warnings(project, folder=None):
    """Report competing names in the selected round or at the project output root."""
    conflicts = set()
    from projfile import never_read_guard

    blocked = never_read_guard(project or {}, None)

    def inspect(directory, candidates):
        found = [n for n in candidates if not blocked(os.path.join(directory, n))
                 and os.path.exists(os.path.join(directory, n))]
        if len(found) > 1:
            conflicts.add((directory, *found))

    base = (project or {}).get('reviewOutDir')
    if base:
        for kind in ('decisions', 'fixList', 'ledger', 'beforeFix', 'fixDir'):
            inspect(base, names(project, kind))
    if folder and not blocked(folder) and os.path.isdir(folder):
        for kind in ('cost', 'expand'):
            inspect(folder, names(project, kind))
        for name in os.listdir(folder):
            if is_review_markdown(name, project):
                inspect(folder, report_aliases(project, name))
            if name.endswith(('.draft.md', '.草稿.md')):
                suffix = '.draft.md' if name.endswith('.draft.md') else '.草稿.md'
                stem = name[:-len(suffix)]
                order = ('.draft.md', '.草稿.md') if language(project) == 'en' else ('.草稿.md', '.draft.md')
                inspect(folder, [stem + s for s in order])
    return ['Multiple names in %s: %s (using %s)' % (d, ', '.join(files), files[0])
            for d, *files in sorted(conflicts)]
