@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

REM Run parameter table generator before building docs
python "%~dp0generate_eval_param_table.py"

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

if "%1" == "" goto help
if "%1" == "help" goto help
if "%1" == "clean" goto clean
if "%1" == "html" goto html
if "%1" == "clean-html" goto clean-html

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:clean
echo.Removing build directory...
if exist %BUILDDIR% rmdir /s /q %BUILDDIR%
echo.Build directory removed.
goto end

:html
echo.Building HTML documentation...
%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%/html %SPHINXOPTS% %O%
if errorlevel 1 (
    echo.
    echo.Build failed. Please check the error messages above.
) else (
    echo.
    echo.Build succeeded! The HTML pages are in %BUILDDIR%/html.
)
goto end

:clean-html
echo.Removing build directory...
if exist %BUILDDIR% rmdir /s /q %BUILDDIR%
echo.Build directory removed.
echo.Building HTML documentation...
%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%/html %SPHINXOPTS% %O%
if errorlevel 1 (
    echo.
    echo.Build failed. Please check the error messages above.
) else (
    echo.
    echo.Build succeeded! The HTML pages are in %BUILDDIR%/html.
)
goto end

:help
echo.Please use one of the following commands:
echo.
echo.  html       to make standalone HTML files
echo.  clean      to clean the build directory
echo.  clean-html to clean the build directory and then build HTML files
echo.  help       to show this help message
echo.
echo.For other Sphinx commands, run: %SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR%

:end
popd