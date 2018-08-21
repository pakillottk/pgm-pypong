import sys, pygame, math, random

def vec2_norm(vec):
    x,y = vec
    return math.sqrt( x*x+y*y )

def normalize_vec2(vec):
    x,y = vec
    norm = vec2_norm( vec )
    return x/norm, y/norm

def vec2_multScalar(vec, scalar):
    x,y = vec
    return x*scalar, y*scalar

def vec2_diff( vecA, vecB ):
    ax,ay = vecA
    bx,by = vecB
    return ax - bx, ay - by

def vec2_dot( vecA, vecB ):
    ax,ay = vecA
    bx,by = vecB
    return ax*bx+ay*by

def reflect_vec2( axis, vec ):
    #just for safety
    axis = normalize_vec2( axis )
    dot = vec2_dot( axis, vec )
    scaledN = vec2_multScalar( axis, 2*dot )
    return vec2_diff( vec, scaledN )


def randomize_vec( magnitude ):
    x_sign = random.randint(0,1)
    if x_sign == 1:
        x_sign = -1
    else:
        x_sign = 1
    y_sign = random.randint(0,1)
    if y_sign == 1:
        y_sign = -1
    else:
        y_sign = 1
    return vec2_multScalar(normalize_vec2([ random.random()*x_sign, random.random()*y_sign ]), magnitude)

def box_test( boxA, boxB ):
    ax, ay, aw, ah = boxA
    bx, by, bw, bh = boxB
    return (abs(ax - bx) * 2 < (aw + bw)) and (abs(ay - by) * 2 < (ah + bh))

pygame.init()
pygame.display.set_caption('PGM - PyPong')
pygame.font.init()
textfont = pygame.font.SysFont('Calibri', 60)

size = width, height = 320, 240
screen = pygame.display.set_mode( size )
black = 0, 0, 0
white = 255, 255, 255

p1 = [5, 70]
p2 = [305, 70]
PLAYER_HEIGHT = 50
PLAYER_WIDTH = 10
PLAYER_SPEED = 5

p1_score = 0
p2_score = 0

ball = [160,120]
BALL_SIZE = 10
BALL_ACCEL = 0.05
BALL_INIT_SPEED = 2
ball_speed = BALL_INIT_SPEED
ball_velocity = randomize_vec( ball_speed )

def player_as_rect( player ):
    x, y = player
    return ( x, y, PLAYER_WIDTH, PLAYER_HEIGHT )

def ball_as_rect( ball ):
    x, y = ball
    return (x, y, BALL_SIZE, BALL_SIZE)

def reset_ball():
    return [160,120]

def render_borders():
    pygame.draw.line(screen, white, (0,0),(width,0),4)
    pygame.draw.line(screen, white, (0,height-2),(width,height-2),4)

def render_separator():
    pygame.draw.line(screen, white, (width/2,0),(width/2,height),4)

def render_scores( score1, score2 ):
    sc1sfc = textfont.render( score1, False, white )
    screen.blit( sc1sfc, ((width/2)-60, 5) )
    sc2sfc = textfont.render( score2, False, white )
    screen.blit( sc2sfc, ((width/2)+30, 5) )

def render_player( player ):
    pygame.draw.rect( screen, white, player_as_rect( player ), 0 )

def render_ball( ball ):
    pygame.draw.rect( screen, white, ball_as_rect( ball ), 0 )

def update_pos( pos, velocity ):
    x, y = pos
    vel_x, vel_y = velocity
    newPos = [ x+vel_x, y+vel_y ]
    return newPos

def update_ball( ball, velocity, speed ):
    return update_pos( ball,  vec2_multScalar( velocity, speed ) )

def update_player( player, direction, speed ):
    newPos = update_pos( player, vec2_multScalar( [0, direction], speed ) )
    newPosTail = [newPos[0],newPos[1]+PLAYER_HEIGHT]
    if in_bounds( newPos ) == 'in' and in_bounds( newPosTail ) == 'in':
        return newPos
    return player

def in_bounds( pos ):
    x,y = pos
    if x <= 0:
        return 'l'
    elif x>=width:
        return 'r'
    elif y<=0:
        return 'u'
    elif y>=height:
        return 'd'

    return 'in'    

def check_collisions( ball, player1, player2 ):
    if box_test( ball_as_rect( ball ), player_as_rect( player1 ) ):
        return 'p1'
    elif box_test( ball_as_rect( ball ), player_as_rect( player2 ) ):
        return 'p2'
    return None

def ball_update_trajectory( velocity, collideWith ):
    if collideWith == 'p1':
        return reflect_vec2( [-1,0],  velocity )
    elif collideWith == 'p2':
        return reflect_vec2( [1,0],  velocity )
    elif collideWith == 'u':
        return reflect_vec2( [0,1],  velocity )
    elif collideWith == 'd':
        return reflect_vec2( [0,-1],  velocity )

def update_input():
    dir1 = 0
    dir2 = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        dir1 = dir1 - 1
    if keys[pygame.K_s]:
        dir1 = dir1 + 1
    if keys[pygame.K_UP]:
        dir2 = dir2 - 1
    if keys[pygame.K_DOWN]:
        dir2 = dir2 + 1
    return dir1, dir2

dt = 0
frameTime = int((1.0/60.0)*1000) #60 FPS
while 1:
    eT = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    dir1, dir2 = update_input()
    p1 = update_player( p1, dir1, PLAYER_SPEED ) 
    p2 = update_player( p2, dir2, PLAYER_SPEED )   

    collision = check_collisions( ball, p1, p2 ) 
    if collision:
        ball_velocity = ball_update_trajectory( ball_velocity, collision )
        ball_speed = ball_speed + BALL_ACCEL
    ball = update_ball( ball, ball_velocity, ball_speed )

    exit_plane = in_bounds( ball )
    if not exit_plane == 'in':
        if exit_plane in 'lr':
            ball = reset_ball( )
            ball_speed = BALL_INIT_SPEED
            ball_velocity = randomize_vec( ball_speed )
            if exit_plane == 'l':
                p2_score = p2_score + 1
            else:
                p1_score = p1_score + 1
        else:
            ball_velocity = ball_update_trajectory( ball_velocity, exit_plane )

    screen.fill( black )
    render_borders()
    render_separator()
    render_scores( str(p1_score), str(p2_score) )

    render_player( p1 )
    render_player( p2 )
    render_ball( ball )

    pygame.display.update()

    fT = pygame.time.get_ticks()
    dt = fT - eT
    pygame.time.wait( frameTime - dt )