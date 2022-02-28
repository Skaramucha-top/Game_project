# Pyganim (pyganim.py, ver 1)
# A sprite animation module for Pygame.
#
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pyganim
# Released under a "Simplified BSD" license
#
# There's a tutorial (and sample code) on how to use this library at http://inventwithpython.com/pyganim
# NOTE: This module requires Pygame to be installed to use. Download it from http://pygame.org
#
# This should be compatible with both Python 2 and Python 3. Please email any
# bug reports to Al at al@inventwithpython.com
#


# TODO: Feature idea: if the same image file is specified, re-use the Surface object. (Make this optional though.)

import pygame, time

# setting up constants
PLAYING = 'playing'
PAUSED = 'paused'
STOPPED = 'stopped'

# These values are used in the anchor() method.
NORTHWEST = 'northwest'
NORTH = 'north'
NORTHEAST = 'northeast'
WEST = 'west'
CENTER = 'center'
EAST = 'east'
SOUTHWEST = 'southwest'
SOUTH = 'south'
SOUTHEAST = 'southeast'


class PygAnimation(object):
    def __init__(self, frames, loop=True):
        # Constructor function for the animation object. Starts off in the STOPPED state.
        #
        # @param frames
        #     A list of tuples for each frame of animation, in one of the following format:
        #       (image_of_frame<pygame.Surface>, duration_in_seconds<int>)
        #       (filename_of_image<str>, duration_in_seconds<int>)
        #     Note that the images and duration cannot be changed. A new PygAnimation object
        #     will have to be created.
        # @param loop Tells the animation object to keep playing in a loop.

        # _images stores the pygame.Surface objects of each frame
        self._images = []
        # _durations stores the durations (in seconds) of each frame.
        # e.g. [1, 1, 2.5] means the first and second frames last one second,
        # and the third frame lasts for two and half seconds.
        self._durations = []
        # _startTimes shows when each frame begins. len(self._startTimes) will
        # always be one more than len(self._images), because the last number
        # will be when the last frame ends, rather than when it starts.
        # The values are in seconds.
        # So self._startTimes[-1] tells you the length of the entire animation.
        # e.g. if _durations is [1, 1, 2.5], then _startTimes will be [0, 1, 2, 4.5]
        self._startTimes = None

        # if the sprites are transformed, the originals are kept in _images
        # and the transformed sprites are kept in _transformedImages.
        self._transformedImages = []

        self._state = STOPPED # The state is always either PLAYING, PAUSED, or STOPPED
        self._loop = loop # If True, the animation will keep looping. If False, the animation stops after playing once.
        self._rate = 1.0 # 2.0 means play the animation twice as fast, 0.5 means twice as slow
        self._visibility = True # If False, then nothing is drawn when the blit() methods are called

        self._playingStartTime = 0 # the time that the play() function was last called.
        self._pausedStartTime = 0 # the time that the pause() function was last called.

        if frames != '_copy': # ('_copy' is passed for frames by the getCopies() method)
            self.numFrames = len(frames)
            assert self.numFrames > 0, 'Must contain at least one frame.'
            for i in range(self.numFrames):
                # load each frame of animation into _images
                frame = frames[i]
                assert type(frame) in (list, tuple) and len(frame) == 2, 'Frame %s has incorrect format.' % (i)
                assert type(frame[0]) in (str, pygame.Surface), 'Frame %s image must be a string filename or a pygame.Surface' % (i)
                assert frame[1] > 0, 'Frame %s duration must be greater than zero.' % (i)
                if type(frame[0]) == str:
                    frame = (pygame.image.load(frame[0]), frame[1])
                self._images.append(frame[0])
                self._durations.append(frame[1])
            self._startTimes = self._getStartTimes()


    def _getStartTimes(self):
        # Internal method to get the start times based off of the _durations list.
        # Don't call this method.
        startTimes = [0]
        for i in range(self.numFrames):
            startTimes.append(startTimes[-1] + self._durations[i])
        return startTimes


    def reverse(self):
        # Reverses the order of the animations.
        self.elapsed = self._startTimes[-1] - self.elapsed
        self._images.reverse()
        self._transformedImages.reverse()
        self._durations.reverse()


    def getCopy(self):

        return self.getCopies(1)[0]


    def getCopies(self, numCopies=1):

        retval = []
        for i in range(numCopies):
            newAnim = PygAnimation('_copy', loop=self.loop)
            newAnim._images = self._images[:]
            newAnim._transformedImages = self._transformedImages[:]
            newAnim._durations = self._durations[:]
            newAnim._startTimes = self._startTimes[:]
            newAnim.numFrames = self.numFrames
            retval.append(newAnim)
        return retval


    def blit(self, destSurface, dest):

        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frameNum = findStartTime(self._startTimes, self.elapsed)
        destSurface.blit(self.getFrame(frameNum), dest)


    def getFrame(self, frameNum):

        if self._transformedImages == []:
            return self._images[frameNum]
        else:
            return self._transformedImages[frameNum]


    def getCurrentFrame(self):

        return self.getFrame(self.currentFrameNum)


    def clearTransforms(self):

        self._transformedImages = []

    def makeTransformsPermanent(self):
        self._images = [pygame.Surface(surfObj.get_size(), 0, surfObj) for surfObj in self._transformedImages]
        for i in range(len(self._transformedImages)):
            self._images[i].blit(self._transformedImages[i], (0,0))

    def blitFrameNum(self, frameNum, destSurface, dest):

        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        destSurface.blit(self.getFrame(frameNum), dest)


    def blitFrameAtTime(self, elapsed, destSurface, dest):

        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frameNum = findStartTime(self._startTimes, elapsed)
        destSurface.blit(self.getFrame(frameNum), dest)


    def isFinished(self):

        return not self.loop and self.elapsed >= self._startTimes[-1]


    def play(self, startTime=None):


        if startTime is None:
            startTime = time.time()

        if self._state == PLAYING:
            if self.isFinished():

                self._playingStartTime = startTime
        elif self._state == STOPPED:

            self._playingStartTime = startTime
        elif self._state == PAUSED:

            self._playingStartTime = startTime - (self._pausedStartTime - self._playingStartTime)
        self._state = PLAYING


    def pause(self, startTime=None):


        if startTime is None:
            startTime = time.time()

        if self._state == PAUSED:
            return
        elif self._state == PLAYING:
            self._pausedStartTime = startTime
        elif self._state == STOPPED:
            rightNow = time.time()
            self._playingStartTime = rightNow
            self._pausedStartTime = rightNow
        self._state = PAUSED


    def stop(self):

        if self._state == STOPPED:
            return
        self._state = STOPPED


    def togglePause(self):


        if self._state == PLAYING:
            if self.isFinished():

                self.play()
            else:
                self.pause()
        elif self._state in (PAUSED, STOPPED):
            self.play()


    def areFramesSameSize(self):

        width, height = self.getFrame(0).get_size()
        for i in range(len(self._images)):
            if self.getFrame(i).get_size() != (width, height):
                return False
        return True


    def getMaxSize(self):

        frameWidths = []
        frameHeights = []
        for i in range(len(self._images)):
            frameWidth, frameHeight = self._images[i].get_size()
            frameWidths.append(frameWidth)
            frameHeights.append(frameHeight)
        maxWidth = max(frameWidths)
        maxHeight = max(frameHeights)

        return (maxWidth, maxHeight)


    def getRect(self):

        maxWidth, maxHeight = self.getMaxSize()
        return pygame.Rect(0, 0, maxWidth, maxHeight)


    def anchor(self, anchorPoint=NORTHWEST):

        if self.areFramesSameSize():
            return # nothing needs to be anchored


        self.clearTransforms() # clears transforms since this method anchors the original images.

        maxWidth, maxHeight = self.getMaxSize()
        halfMaxWidth = int(maxWidth / 2)
        halfMaxHeight = int(maxHeight / 2)

        for i in range(len(self._images)):
            # go through and copy all frames to a max-sized Surface object
            # NOTE: This makes changes to the original images in self._images, not the transformed images in self._transformedImages
            newSurf = pygame.Surface((maxWidth, maxHeight)) # TODO: this is probably going to have errors since I'm using the default depth.

            # set the expanded areas to be transparent
            newSurf = newSurf.convert_alpha()
            newSurf.fill((0,0,0,0))

            frameWidth, frameHeight = self._images[i].get_size()
            halfFrameWidth = int(frameWidth / 2)
            halfFrameHeight = int(frameHeight / 2)

            # position the Surface objects to the specified anchor point
            if anchorPoint == NORTHWEST:
                newSurf.blit(self._images[i], (0, 0))
            elif anchorPoint == NORTH:
                newSurf.blit(self._images[i], (halfMaxWidth - halfFrameWidth, 0))
            elif anchorPoint == NORTHEAST:
                newSurf.blit(self._images[i], (maxWidth - frameWidth, 0))
            elif anchorPoint == WEST:
                newSurf.blit(self._images[i], (0, halfMaxHeight - halfFrameHeight))
            elif anchorPoint == CENTER:
                newSurf.blit(self._images[i], (halfMaxWidth - halfFrameWidth, halfMaxHeight - halfFrameHeight))
            elif anchorPoint == EAST:
                newSurf.blit(self._images[i], (maxWidth - frameWidth, halfMaxHeight - halfFrameHeight))
            elif anchorPoint == SOUTHWEST:
                newSurf.blit(self._images[i], (0, maxHeight - frameHeight))
            elif anchorPoint == SOUTH:
                newSurf.blit(self._images[i], (halfMaxWidth - halfFrameWidth, maxHeight - frameHeight))
            elif anchorPoint == SOUTHEAST:
                newSurf.blit(self._images[i], (maxWidth - frameWidth, maxHeight - frameHeight))
            self._images[i] = newSurf


    def nextFrame(self, jump=1):
        # Set the elapsed time to the beginning of the next frame.
        # You can jump ahead by multiple frames by specifying a different
        # argument for jump.
        # Negative values have the same effect as calling prevFrame()
        self.currentFrameNum += int(jump)


    def prevFrame(self, jump=1):

        self.currentFrameNum -= int(jump)


    def rewind(self, seconds=None):
        # Set the elapsed time back relative to the current elapsed time.
        if seconds is None:
            self.elapsed = 0.0
        else:
            self.elapsed -= seconds


    def fastForward(self, seconds=None):
        # Set the elapsed time forward relative to the current elapsed time.
        if seconds is None:
            self.elapsed = self._startTimes[-1] - 0.00002 # done to compensate for rounding errors
        else:
            self.elapsed += seconds

    def _makeTransformedSurfacesIfNeeded(self):
        # Internal-method. Creates the Surface objects for the _transformedImages list.
        # Don't call this method.
        if self._transformedImages == []:
            self._transformedImages = [surf.copy() for surf in self._images]


    # Transformation methods.
    # (These are analogous to the pygame.transform.* functions, except they
    # are applied to all frames of the animation object.
    def flip(self, xbool, ybool):
        # Flips the image horizontally, vertically, or both.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.flip
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.flip(self.getFrame(i), xbool, ybool)


    def scale(self, width_height):

        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.scale(self.getFrame(i), width_height)


    def rotate(self, angle):
        # Rotates the image.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotate
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.rotate(self.getFrame(i), angle)


    def rotozoom(self, angle, scale):
        # Rotates and scales the image simultaneously.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotozoom
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.rotozoom(self.getFrame(i), angle, scale)


    def scale2x(self):

        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.scale2x(self.getFrame(i))


    def smoothscale(self, width_height):

        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.smoothscale(self.getFrame(i), width_height)

    def _surfaceMethodWrapper(self, wrappedMethodName, *args, **kwargs):
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            methodToCall = getattr(self._transformedImages[i], wrappedMethodName)
            methodToCall(*args, **kwargs)

    # There's probably a more terse way to generate the following methods,
    # but I don't want to make the code even more unreadable.
    def convert(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.convert
        self._surfaceMethodWrapper('convert', *args, **kwargs)


    def convert_alpha(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.convert_alpha
        self._surfaceMethodWrapper('convert_alpha', *args, **kwargs)


    def set_alpha(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_alpha
        self._surfaceMethodWrapper('set_alpha', *args, **kwargs)


    def scroll(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.scroll
        self._surfaceMethodWrapper('scroll', *args, **kwargs)


    def set_clip(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_clip
        self._surfaceMethodWrapper('set_clip', *args, **kwargs)


    def set_colorkey(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_colorkey
        self._surfaceMethodWrapper('set_colorkey', *args, **kwargs)


    def lock(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.unlock
        self._surfaceMethodWrapper('lock', *args, **kwargs)


    def unlock(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.lock
        self._surfaceMethodWrapper('unlock', *args, **kwargs)



    # Getter and setter methods for properties
    def _propGetRate(self):
        return self._rate

    def _propSetRate(self, rate):
        rate = float(rate)
        if rate < 0:
            raise ValueError('rate must be greater than 0.')
        self._rate = rate

    rate = property(_propGetRate, _propSetRate)


    def _propGetLoop(self):
        return self._loop

    def _propSetLoop(self, loop):
        if self.state == PLAYING and self._loop and not loop:

            self._playingStartTime = time.time() - self.elapsed
        self._loop = bool(loop)

    loop = property(_propGetLoop, _propSetLoop)


    def _propGetState(self):
        if self.isFinished():
            self._state = STOPPED # if finished playing, then set state to STOPPED.

        return self._state

    def _propSetState(self, state):
        if state not in (PLAYING, PAUSED, STOPPED):
            raise ValueError('state must be one of pyganim.PLAYING, pyganim.PAUSED, or pyganim.STOPPED')
        if state == PLAYING:
            self.play()
        elif state == PAUSED:
            self.pause()
        elif state == STOPPED:
            self.stop()

    state = property(_propGetState, _propSetState)


    def _propGetVisibility(self):
        return self._visibility

    def _propSetVisibility(self, visibility):
        self._visibility = bool(visibility)

    visibility = property(_propGetVisibility, _propSetVisibility)


    def _propSetElapsed(self, elapsed):
        # NOTE: Do to floating point rounding errors, this doesn't work precisely.
        elapsed += 0.00001 # done to compensate for rounding errors

        if self._loop:
            elapsed = elapsed % self._startTimes[-1]
        else:
            elapsed = getInBetweenValue(0, elapsed, self._startTimes[-1])

        rightNow = time.time()
        self._playingStartTime = rightNow - (elapsed * self.rate)

        if self.state in (PAUSED, STOPPED):
            self.state = PAUSED # if stopped, then set to paused
            self._pausedStartTime = rightNow


    def _propGetElapsed(self):

        if self._state == STOPPED:
            # if stopped, then just return 0
            return 0

        if self._state == PLAYING:

            elapsed = (time.time() - self._playingStartTime) * self.rate
        elif self._state == PAUSED:
            # if paused, then draw the frame that was playing at the time the
            # PygAnimation object was paused
            elapsed = (self._pausedStartTime - self._playingStartTime) * self.rate
        if self._loop:
            elapsed = elapsed % self._startTimes[-1]
        else:
            elapsed = getInBetweenValue(0, elapsed, self._startTimes[-1])
        elapsed += 0.00001 # done to compensate for rounding errors
        return elapsed

    elapsed = property(_propGetElapsed, _propSetElapsed)


    def _propGetCurrentFrameNum(self):

        return findStartTime(self._startTimes, self.elapsed)


    def _propSetCurrentFrameNum(self, frameNum):
        # Change the elapsed time to the beginning of a specific frame.
        if self.loop:
            frameNum = frameNum % len(self._images)
        else:
            frameNum = getInBetweenValue(0, frameNum, len(self._images)-1)
        self.elapsed = self._startTimes[frameNum]

    currentFrameNum = property(_propGetCurrentFrameNum, _propSetCurrentFrameNum)



class PygConductor(object):
    def __init__(self, *animations):
        assert len(animations) > 0, 'at least one PygAnimation object is required'

        self._animations = []
        self.add(*animations)


    def add(self, *animations):
        if type(animations[0]) == dict:
            for k in animations[0].keys():
                self._animations.append(animations[0][k])
        elif type(animations[0]) in (tuple, list):
            for i in range(len(animations[0])):
                self._animations.append(animations[0][i])
        else:
            for i in range(len(animations)):
                self._animations.append(animations[i])

    def _propGetAnimations(self):
        return self._animations

    def _propSetAnimations(self, val):
        self._animations = val

    animations = property(_propGetAnimations, _propSetAnimations)

    def play(self, startTime=None):
        if startTime is None:
            startTime = time.time()

        for animObj in self._animations:
            animObj.play(startTime)

    def pause(self, startTime=None):
        if startTime is None:
            startTime = time.time()

        for animObj in self._animations:
            animObj.pause(startTime)

    def stop(self):
        for animObj in self._animations:
            animObj.stop()

    def reverse(self):
        for animObj in self._animations:
            animObj.reverse()

    def clearTransforms(self):
        for animObj in self._animations:
            animObj.clearTransforms()

    def makeTransformsPermanent(self):
        for animObj in self._animations:
            animObj.makeTransformsPermanent()

    def togglePause(self):
        for animObj in self._animations:
            animObj.togglePause()

    def nextFrame(self, jump=1):
        for animObj in self._animations:
            animObj.nextFrame(jump)

    def prevFrame(self, jump=1):
        for animObj in self._animations:
            animObj.prevFrame(jump)

    def rewind(self, seconds=None):
        for animObj in self._animations:
            animObj.rewind(seconds)

    def fastForward(self, seconds=None):
        for animObj in self._animations:
            animObj.fastForward(seconds)

    def flip(self, xbool, ybool):
        for animObj in self._animations:
            animObj.flip(xbool, ybool)

    def scale(self, width_height):
        for animObj in self._animations:
            animObj.scale(width_height)

    def rotate(self, angle):
        for animObj in self._animations:
            animObj.rotate(angle)

    def rotozoom(self, angle, scale):
        for animObj in self._animations:
            animObj.rotozoom(angle, scale)

    def scale2x(self):
        for animObj in self._animations:
            animObj.scale2x()

    def smoothscale(self, width_height):
        for animObj in self._animations:
            animObj.smoothscale(width_height)

    def convert(self):
        for animObj in self._animations:
            animObj.convert()

    def convert_alpha(self):
        for animObj in self._animations:
            animObj.convert_alpha()

    def set_alpha(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_alpha(*args, **kwargs)

    def scroll(self, dx=0, dy=0):
        for animObj in self._animations:
            animObj.scroll(dx, dy)

    def set_clip(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_clip(*args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_colorkey(*args, **kwargs)

    def lock(self):
        for animObj in self._animations:
            animObj.lock()

    def unlock(self):
        for animObj in self._animations:
            animObj.unlock()


def getInBetweenValue(lowerBound, value, upperBound):

    if value < lowerBound:
        return lowerBound
    elif value > upperBound:
        return upperBound
    return value


def findStartTime(startTimes, target):

    assert startTimes[0] == 0
    lb = 0 # "lb" is lower bound
    ub = len(startTimes) - 1 # "ub" is upper bound

    # handle special cases:
    if len(startTimes) == 0:
        return 0
    if target >= startTimes[-1]:
        return ub - 1

    # perform binary search:
    while True:
        i = int((ub - lb) / 2) + lb

        if startTimes[i] == target or (startTimes[i] < target and startTimes[i+1] > target):
            if i == len(startTimes):
                return i - 1
            else:
                return i

        if startTimes[i] < target:
            lb = i
        elif startTimes[i] > target:
            ub = i
