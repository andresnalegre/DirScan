import os
from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


_IGNORED_FOLDERS: FrozenSet[str] = frozenset({
    'node_modules', '.pnp', '.yarn', '.npm', '.pnpm-store',
    'venv', '.venv', 'env', 'virtualenv', '.virtualenv',
    '__pycache__', '.tox', '.nox', 'site-packages', 'dist-packages',
    '.pdm-build', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.dmypy',
    '.hypothesis',
    '.bundle',
    '.gradle', '.m2', '.ivy2', '.kotlin', 'target',
    'Pods', 'DerivedData', 'xcuserdata',
    'packages', 'obj',
    '.stack-work', 'dist-newstyle',
    '.next', '.nuxt', '.svelte-kit', '.remix', '__sapper__',
    'storybook-static', '.expo', '.expo-shared', '.vite',
    '.cache', '.parcel-cache', '.turbo', '.swc',
    '.webpack', '.rollup.cache', '.astro', '.angular',
    '.sass-cache', '.eslintcache', '.stylelintcache',
    '.git', '.svn', '.hg', '.bzr', '_darcs', '.fossil', '.jj',
    '.idea', '.vscode', '.vs', '.eclipse',
    '.project', '.settings', '.classpath', '.factorypath',
    '.metals', '.bloop', '.zed',
    '.Trash', '.Trashes', '.Spotlight-V100', '.fseventsd',
    '.DocumentRevisions-V100', '.TemporaryItems',
    '.MobileBackups', '.hotfiles.btree',
    '$RECYCLE.BIN', 'System Volume Information', 'RECYCLER', 'RECYCLED',
    '.thumbnails',
    'tmp', 'temp', '.tmp', '.temp',
    '.terraform', '.terragrunt-cache', '.vagrant', '.ansible',
    '.pulumi', '.serverless',
    'coverage', '.nyc_output', 'htmlcov', '.coverage_html',
    'test-results', 'test-reports',
    'allure-results', 'allure-report', 'playwright-report',
    '__snapshots__',
})

_IGNORED_FILENAMES: FrozenSet[str] = frozenset({
    '.DS_Store', '.AppleDouble', '.LSOverride',
    'Thumbs.db', 'ehthumbs.db', 'ehthumbs_vista.db', 'Desktop.ini',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'Gemfile.lock', 'Cargo.lock', 'composer.lock',
    'poetry.lock', 'Pipfile.lock', 'mix.lock', 'pubspec.lock',
    'go.sum', 'flake.lock',
    'map.txt',
})

_IGNORED_EXTENSIONS: FrozenSet[str] = frozenset({
    '.pyc', '.pyo', '.pyd',
    '.class',
    '.o', '.obj', '.lo', '.la',
    '.a', '.lib',
    '.so', '.dll', '.dylib',
    '.exe', '.com',
    '.swp', '.swo', '.swn',
    '.bak',
    '.prof',
    '.map',
    '.min.js', '.min.css',
    '.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz', '.rar', '.7z', '.lz4', '.zst',
    '.dmg', '.iso', '.img',
    '.pem', '.key', '.p12', '.pfx', '.cer', '.crt', '.der', '.p8',
    '.wasm',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
})

_IGNORED_PREFIXES: Tuple[str, ...] = (
    '._',
    '.~lock.',
)

_IGNORED_SUFFIXES: Tuple[str, ...] = (
    '~',
)

_KEEP_DOTFILES: FrozenSet[str] = frozenset({
    '.gitignore', '.gitattributes', '.gitmodules',
    '.editorconfig',
    '.prettierrc', '.prettierignore',
    '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintignore',
    '.stylelintrc',
    '.babelrc',
    '.browserslistrc',
    '.npmrc', '.yarnrc', '.pnpmfile.cjs',
    '.dockerignore',
    '.htaccess',
    '.env', '.env.local', '.env.example', '.env.sample', '.env.template',
    '.flake8', '.pylintrc', '.pep8',
    '.rubocop.yml',
    '.travis.yml',
    '.coverage',
    'Dockerfile',
})


def get_ignored_folders() -> FrozenSet[str]:
    return _IGNORED_FOLDERS

def get_ignored_filenames() -> FrozenSet[str]:
    return _IGNORED_FILENAMES

def get_ignored_extensions() -> FrozenSet[str]:
    return _IGNORED_EXTENSIONS

def get_ignored_prefixes() -> Tuple[str, ...]:
    return _IGNORED_PREFIXES

def get_ignored_suffixes() -> Tuple[str, ...]:
    return _IGNORED_SUFFIXES

def get_keep_dotfiles() -> FrozenSet[str]:
    return _KEEP_DOTFILES


@dataclass
class FilterConfig:
    folders:    FrozenSet[str]   = field(default_factory=frozenset)
    filenames:  FrozenSet[str]   = field(default_factory=frozenset)
    extensions: FrozenSet[str]   = field(default_factory=frozenset)
    prefixes:   Tuple[str, ...]  = field(default_factory=tuple)
    suffixes:   Tuple[str, ...]  = field(default_factory=tuple)

    @classmethod
    def default(cls) -> "FilterConfig":
        return cls(
            folders    = _IGNORED_FOLDERS,
            filenames  = _IGNORED_FILENAMES,
            extensions = _IGNORED_EXTENSIONS,
            prefixes   = _IGNORED_PREFIXES,
            suffixes   = _IGNORED_SUFFIXES,
        )

    def filter_folder(self, name: str) -> bool:
        return name not in self.folders

    def filter_file(self, name: str) -> bool:
        if name in _KEEP_DOTFILES:
            return True
        if name in self.filenames:
            return False
        for p in self.prefixes:
            if name.startswith(p):
                return False
        for s in self.suffixes:
            if name.endswith(s):
                return False
        if name.startswith('.') and name not in _KEEP_DOTFILES:
            return False
        lower = name.lower()
        for ext in self.extensions:
            if lower.endswith(ext):
                return False
        return True


ALL_CATEGORIES = [
    {
        "key":   "deps",
        "icon":  "📦",
        "name":  "Dependency Folders",
        "desc":  "Package/dependency directories that are auto-installed.\nNever part of your source code.",
        "items": {item: "folder" for item in {
            'node_modules', '.pnp', '.yarn', '.npm', '.pnpm-store',
            'venv', '.venv', 'env', 'virtualenv', '.virtualenv',
            'site-packages', 'dist-packages', '.bundle',
            '.gradle', '.m2', '.ivy2', 'Pods', 'packages',
        }},
    },
    {
        "key":   "build",
        "icon":  "🔨",
        "name":  "Build & Cache",
        "desc":  "Compiled output, caches, and generated build artefacts.\nEverything here is derived from your source.",
        "items": {item: "folder" for item in {
            '__pycache__', '.tox', '.nox', '.pdm-build', '.pytest_cache',
            '.mypy_cache', '.ruff_cache', '.dmypy', '.hypothesis',
            '.kotlin', 'target', 'DerivedData', 'xcuserdata', 'obj',
            '.stack-work', 'dist-newstyle',
            '.next', '.nuxt', '.svelte-kit', '.remix', '__sapper__',
            'storybook-static', '.expo', '.expo-shared', '.vite',
            '.cache', '.parcel-cache', '.turbo', '.swc',
            '.webpack', '.rollup.cache', '.astro', '.angular',
            '.sass-cache', '.eslintcache', '.stylelintcache',
            'tmp', 'temp', '.tmp', '.temp',
            '.terraform', '.terragrunt-cache', '.vagrant', '.ansible',
            '.pulumi', '.serverless',
            'coverage', '.nyc_output', 'htmlcov', '.coverage_html',
            'test-results', 'test-reports',
            'allure-results', 'allure-report', 'playwright-report',
            '__snapshots__',
        }},
    },
    {
        "key":   "vcs",
        "icon":  "🔧",
        "name":  "Version Control & IDE",
        "desc":  "Internal folders created by Git, SVN, and editors.\nTool internals — not project content.",
        "items": {item: "folder" for item in {
            '.git', '.svn', '.hg', '.bzr', '_darcs', '.fossil', '.jj',
            '.idea', '.vscode', '.vs', '.eclipse',
            '.project', '.settings', '.classpath', '.factorypath',
            '.metals', '.bloop', '.zed',
        }},
    },
    {
        "key":   "os",
        "icon":  "🗂",
        "name":  "OS & System Junk",
        "desc":  "Files and folders created by macOS, Windows, and Linux.\nNone of these are intentional project files.",
        "items": {
            **{item: "folder" for item in {
                '.Trash', '.Trashes', '.Spotlight-V100', '.fseventsd',
                '.DocumentRevisions-V100', '.TemporaryItems',
                '.MobileBackups', '.hotfiles.btree',
                '$RECYCLE.BIN', 'System Volume Information', 'RECYCLER', 'RECYCLED',
                '.thumbnails',
            }},
            **{item: "file" for item in {
                '.DS_Store', '.AppleDouble', '.LSOverride',
                'Thumbs.db', 'ehthumbs.db', 'ehthumbs_vista.db', 'Desktop.ini',
            }},
        },
    },
    {
        "key":   "locks",
        "icon":  "🔒",
        "name":  "Lock Files",
        "desc":  "Auto-generated lock files derived from your package manifests.\nThe manifest (package.json, Pipfile…) is what matters.",
        "items": {item: "file" for item in {
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'Gemfile.lock', 'Cargo.lock', 'composer.lock',
            'poetry.lock', 'Pipfile.lock', 'mix.lock', 'pubspec.lock',
            'go.sum', 'flake.lock',
        }},
    },
    {
        "key":   "binary",
        "icon":  "🔩",
        "name":  "Binary & Compiled",
        "desc":  "Compiled bytecode, native objects, minified bundles, archives.\nOutputs of your build process — not source files.",
        "items": {item: "ext" for item in {
            '.pyc', '.pyo', '.pyd', '.class',
            '.o', '.obj', '.lo', '.la', '.a', '.lib',
            '.so', '.dll', '.dylib', '.exe', '.com',
            '.swp', '.swo', '.swn', '.bak', '.prof', '.map',
            '.min.js', '.min.css',
            '.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz',
            '.rar', '.7z', '.lz4', '.zst',
            '.dmg', '.iso', '.img',
            '.pem', '.key', '.p12', '.pfx', '.cer', '.crt', '.der', '.p8',
            '.wasm',
            '.ttf', '.otf', '.woff', '.woff2', '.eot',
        }},
    },
    {
        "key":   "patterns",
        "icon":  "🔍",
        "name":  "File Patterns",
        "desc":  "Filename prefixes/suffixes used by OS and editors for temp/lock files.\ne.g. '._' (macOS resource forks), '~' (editor backups).",
        "items": {
            **{item: "pattern" for item in _IGNORED_PREFIXES},
            **{item: "pattern" for item in _IGNORED_SUFFIXES},
        },
    },
]

PREFIX_SET: FrozenSet[str] = frozenset(_IGNORED_PREFIXES)


def count_items(path: str, config: FilterConfig) -> int:
    total = 0
    try:
        for _root, dirs, files in os.walk(path, followlinks=False):
            dirs[:]  = [d for d in dirs  if config.filter_folder(d)]
            files    = [f for f in files if config.filter_file(f) and f != "map.txt"]
            total   += len(dirs) + len(files)
    except Exception as e:
        print(f"[DirScan] count_items error: {e}")
    return max(total, 1)


def filter_items(items: list, path: str, config: FilterConfig) -> tuple:
    def full_path(name: str) -> str:
        return os.path.join(path, name)

    folders = sorted(
        item for item in items
        if os.path.isdir(full_path(item)) and not os.path.islink(full_path(item))
        and config.filter_folder(item)
    )
    files = sorted(
        item for item in items
        if os.path.isfile(full_path(item)) and not os.path.islink(full_path(item))
        and config.filter_file(item)
    )
    return folders, files