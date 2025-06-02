# tasks/hooks.py
import logging

# Obtener un logger. Puedes usar el logger de tu app 'tasks' o uno específico para hooks.
# Si usas el de 'tasks', asegúrate de que esté configurado en settings.LOGGING.
# Por simplicidad, podemos usar un logger con el nombre de este módulo.
logger = logging.getLogger(__name__)

def print_task_result(task):
    """
    Este es un 'hook function' para Django Q.
    Se llama después de que una tarea asíncrona (que tenga este hook especificado) se completa.
    Registra si la tarea fue exitosa o falló, y su resultado.
    """
    if task.success:
        logger.info(
            f"HOOK: Tarea asíncrona '{task.name}' (ID: {task.id}, Grupo: {task.group or 'N/A'}) "
            f"completada exitosamente. Resultado: {task.result}"
        )
    else:
        # task.result contendrá la excepción o el traceback en caso de fallo.
        logger.error(
            f"HOOK: Tarea asíncrona '{task.name}' (ID: {task.id}, Grupo: {task.group or 'N/A'}) "
            f"FALLÓ. Error/Resultado: {task.result}"
        )
        # También podrías querer loguear task.attempt_count si es relevante