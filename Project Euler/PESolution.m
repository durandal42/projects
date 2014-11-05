//
//  PESolution.m
//  Project Euler
//
//  Created by David Sloan on 7/28/14.
//  Copyright (c) 2014 David Sloan. All rights reserved.
//

#import "PESolution.h"

@interface PESolution()
{
    unsigned long _problemNumber;
}
@end

@implementation PESolution


- (PESolution *) initWithProblemNumber:(unsigned long) problemNumber
{
    self = [super init];
    _problemNumber = problemNumber;
    return self;
}

- (NSString *) description
{
    return [NSString stringWithFormat:@"Problem #%lu", _problemNumber];
}



@end
