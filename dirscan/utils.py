import os

_IGNORED_FOLDERS: frozenset[str] = frozenset({
    '.git', '.svn', '.hg', '.bzr', '_darcs', '.fossil', '.jj',
    'node_modules', '.pnp', '.yarn', '.npm', '.pnpm-store',
    'venv', '.venv', 'env', '.env', 'virtualenv', '.virtualenv',
    '__pycache__', '.tox', '.nox', 'site-packages', 'dist-packages',
    '.pdm-build',
    'vendor', '.bundle',
    '.gradle', '.m2', '.ivy2', '.kotlin',
    'Pods', '.build', 'DerivedData', 'xcuserdata',
    'target',
    'packages', 'obj',
    '_build', 'deps',
    '.stack-work', 'dist-newstyle',
    'build', 'dist', 'out', 'output', 'outputs',
    'bin', 'lib', 'lib64', 'lib32',
    'release', 'debug',
    '.next', '.nuxt', '.svelte-kit', '.remix', '__sapper__',
    'storybook-static', '.expo', '.expo-shared', '.vite',
    '.cache', '.parcel-cache', '.turbo', '.swc',
    '.eslintcache', '.stylelintcache',
    '.pytest_cache', '.mypy_cache', '.ruff_cache', '.dmypy',
    '.hypothesis', '__snapshots__',
    '.sass-cache',
    '.angular',
    'tmp', 'temp', '.tmp', '.temp',
    '.webpack', '.rollup.cache',
    '.astro',
    'coverage', '.nyc_output', 'htmlcov', '.coverage_html',
    'test-results', 'test-reports',
    'allure-results', 'allure-report',
    'playwright-report',
    'screenshots', 'videos',
    '.idea', '.vscode', '.vs', '.eclipse',
    '.project', '.settings', '.classpath', '.factorypath',
    '.metals', '.bloop',
    '.zed',
    '.Trash', '.Trashes',
    '.Spotlight-V100', '.fseventsd',
    '.DocumentRevisions-V100', '.TemporaryItems',
    '.MobileBackups', '.hotfiles.btree',
    '$RECYCLE.BIN', 'System Volume Information',
    'RECYCLER', 'RECYCLED',
    '.thumbnails', '.local/share/Trash',
    '.terraform', '.terragrunt-cache',
    '.vagrant',
    '.ansible',
    '.pulumi',
    '.serverless',
    'logs', 'log',
})

_IGNORED_FILENAMES: frozenset[str] = frozenset({
    '.DS_Store', '.AppleDouble', '.LSOverride',
    'Thumbs.db', 'ehthumbs.db', 'ehthumbs_vista.db', 'Desktop.ini',
    '.env', '.env.local',
    '.coverage', '.coverage.xml',
    'MANIFEST', '.python-version', '.node-version', '.nvmrc', '.tool-versions',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'Gemfile.lock', 'Cargo.lock', 'composer.lock',
    'poetry.lock', 'Pipfile.lock', 'mix.lock', 'pubspec.lock',
    'go.sum', 'flake.lock',
})

_IGNORED_EXTENSIONS: frozenset[str] = frozenset({
    '.pyc', '.pyo', '.pyd',
    '.class',
    '.o', '.obj', '.lo', '.la',
    '.a', '.lib',
    '.so', '.dll', '.dylib',
    '.exe', '.com', '.out',
    '.log', '.tmp', '.temp',
    '.bak', '.orig', '.rej',
    '.swp', '.swo', '.swn',
    '.coverage', '.prof',
    '.map',
    '.min.js', '.min.css',
    '.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz', '.rar', '.7z', '.lz4',
    '.zst',
    '.dmg', '.iso', '.img',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
    '.webp', '.avif', '.heic', '.tiff', '.tif', '.raw',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv',
    '.wav', '.flac', '.aac', '.ogg', '.opus',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.pem', '.key', '.p12', '.pfx', '.cer', '.crt', '.der', '.p8',
    '.db', '.sqlite', '.sqlite3',
    '.wasm',
})

_IGNORED_PREFIXES: tuple[str, ...] = (
    '._',
    '.~lock.',
)

_IGNORED_SUFFIXES: tuple[str, ...] = (
    '~',
    '.orig',
)

_KEEP_DOTFILES: frozenset[str] = frozenset({
    '.gitignore', '.gitattributes', '.gitmodules',
    '.editorconfig',
    '.prettierrc', '.prettierignore',
    '.eslintrc', '.eslintignore',
    '.stylelintrc',
    '.babelrc',
    '.browserslistrc',
    '.npmrc', '.yarnrc', '.pnpmfile.cjs',
    '.dockerignore',
    '.htaccess',
    '.env.example', '.env.sample', '.env.template',
    '.flake8', '.pylintrc', '.pep8',
    '.rubocop.yml',
    '.travis.yml',
    'Dockerfile',
})


class _Filter:
    @staticmethod
    def folder(name: str) -> bool:
        return name not in _IGNORED_FOLDERS

    @staticmethod
    def file(name: str) -> bool:
        if name in _KEEP_DOTFILES:
            return True
        if name in _IGNORED_FILENAMES:
            return False
        for prefix in _IGNORED_PREFIXES:
            if name.startswith(prefix):
                return False
        for suffix in _IGNORED_SUFFIXES:
            if name.endswith(suffix):
                return False
        if name.startswith('.'):
            return False
        lower = name.lower()
        for ext in _IGNORED_EXTENSIONS:
            if lower.endswith(ext):
                return False
        return True


def count_items(path: str, ignore_temp_files: bool = False) -> int:
    total = 0
    try:
        for _root, dirs, files in os.walk(path, followlinks=False):
            if ignore_temp_files:
                dirs[:] = [d for d in dirs if _Filter.folder(d)]
                files   = [f for f in files if _Filter.file(f)]
            else:
                dirs[:] = dirs
            total += len(dirs) + len(files)
    except Exception as e:
        print(f"Error counting items: {e}")
    return max(total, 1)


def filter_items(
    items: list[str],
    path: str,
    ignore_temp_files: bool,
) -> tuple[list[str], list[str]]:
    full = lambda name: os.path.join(path, name)

    folders = sorted(
        i for i in items
        if os.path.isdir(full(i)) and not os.path.islink(full(i))
    )
    files = sorted(
        i for i in items
        if os.path.isfile(full(i)) and not os.path.islink(full(i))
    )

    if ignore_temp_files:
        folders = [f for f in folders if _Filter.folder(f)]
        files   = [f for f in files   if _Filter.file(f)]

    return folders, files