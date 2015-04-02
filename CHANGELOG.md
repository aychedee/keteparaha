# Changelog

## [unreleased] [unreleased]
### Changed
-

## [0.0.17] [2015-04-02]
### Changed
- Bugfix, we handle stale elements when waiting for them to be clickable
- Bugfix, Components can be used to instantiate a page
- Library compatible with Python 2.7+

## [0.0.16] [2015-03-18]
### Changed
-

## [0.0.15] [2015-03-18]
### Changed
- Technique for getting components underlying element improved when the
  component is part of a list/group

## [0.0.14] [2015-03-18]
### Changed
- Clickable components should be visible as well as enabled.
- Components only look inside their parents element for sub_elements

## [0.0.13] [2015-03-17]
### Changed
- Improved proxying to underlying web element, removes some sync related bugs
- Adds our own text in element expectation
- the web element proxy can now get elements by link text or button text

## [0.0.12] [2015-03-15]
### Changed
- Better error message when we cannot find a component in a page

## [0.0.11] 2015-03-13
### Changed
- Only refresh elements that are actually stale when getting text

## [0.0.10] 2015-03-13
### Changed
- Bugfix, components returned by get_components are assigned unique selectors
  using nth-child. This is going to fail if the original selector is not
  specific enough.

## [0.0.9] 2015-03-12
### Changed
- Adds a hover method so that we can trigger dropdowns and the like
- Add a clear method that takes a selector
- Components refresh their element before returning their text
- Adds a has_text method to all pages and components. Remove the assertions
  from the page/component class. These should live in the test case

## [0.0.8] 2015-03-11
### Changed
- Subclasses of component can be passed as the value of the open argument to
a page or components click method.

## [0.0.7] 2015-03-11
### Changed
- Breaking change of the of api to use new automatic page and component
  discovery
- CNAME file so that the project can be found at keteparaha.aychedee.com
- Action methods of Page and Component automatically return the appropriate 
  page or component. Pages and Components are registered using a metaclass 
  mechanism similar to Django's ORM. 
