import pyray as pr
import os
import math

def main():
    pr.init_window(2080, 1440, "Test de Vérité du Drone")
    pr.set_target_fps(60)

    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    chemin_modele = os.path.join(dossier_actuel, "models", "dji_spark.glb")

    drone = pr.load_model(chemin_modele)

    camera = pr.Camera3D()
    camera.up = pr.Vector3(0.0, 1.0, 0.0)
    camera.fovy = 45.0
    camera.projection = pr.CAMERA_PERSPECTIVE
    player_pos = pr.Vector3(0.0, 1.0, 0.0)

    while not pr.window_should_close():

        # --- A. MISE À JOUR ---
        vitesse = 0.2
        if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT): player_pos.x += vitesse
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):  player_pos.x -= vitesse
        if pr.is_key_down(pr.KeyboardKey.KEY_DOWN):  player_pos.z += vitesse
        if pr.is_key_down(pr.KeyboardKey.KEY_UP):    player_pos.z -= vitesse

        camera.target = pr.Vector3(player_pos.x, player_pos.y, player_pos.z)
        camera.position = pr.Vector3(player_pos.x, player_pos.y + 10.0, player_pos.z + 10.0)

        vitesse = 0.2
        if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT): player_pos.x += vitesse
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):  player_pos.x -= vitesse
        if pr.is_key_down(pr.KeyboardKey.KEY_DOWN):  player_pos.z += vitesse
        if pr.is_key_down(pr.KeyboardKey.KEY_UP):    player_pos.z -= vitesse

        temps = pr.get_time()
        hauteur_de_base = 1.0
        
        player_pos.y = hauteur_de_base + (math.sin(temps * 3.0) * 0.5)

        camera.target = pr.Vector3(player_pos.x, player_pos.y, player_pos.z)
        camera.position = pr.Vector3(player_pos.x, player_pos.y + 10.0, player_pos.z + 10.0)

        pr.begin_drawing()
        
        pr.clear_background(pr.WHITE)
        
        pr.begin_mode_3d(camera)
        
        # La grille au sol
        pr.draw_grid(50, 2.0)
        
        # Le modèle "normal" à l'échelle 1.0
        pr.draw_model(drone, player_pos, 0.20, pr.WHITE)

        # La boîte rouge (pour être sûr de l'endroit exact où il devrait être)

        pr.end_mode_3d()
        
        
        pr.end_drawing()


    pr.unload_model(drone)
    pr.close_window()

if __name__ == "__main__":
    main()